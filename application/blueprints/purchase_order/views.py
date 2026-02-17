from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from jinja2 import TemplateNotFound
import json

from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from .models import PurchaseOrder, PurchaseOrderDetail, UserPurchaseOrder
from .forms import Form
from .. raw_material import RawMaterial
from .. measure import Measure
from .. vendor import Vendor
from application.extensions import db, year_first_day, month_last_day, next_control_number
from .. user import login_required, roles_accepted
from . import app_name, app_label


bp = Blueprint(app_name, __name__, template_folder="pages", url_prefix=f"/{app_name}")
ROLES_ACCEPTED = app_label


@bp.route("/", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def home():
    if request.method == "POST":
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
    else:
        date_from = year_first_day()
        date_to = month_last_day()

    purchase_orders = PurchaseOrder.query.filter(
        PurchaseOrder.record_date.between(date_from, date_to)
        ).order_by(
        PurchaseOrder.purchase_order_number.desc()
        ).all()
        

    context = {
        "purchase_orders": purchase_orders,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/pending", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def pending():
    purchase_orders = PurchaseOrder.query.filter(
        PurchaseOrder.cancelled.is_(None),
        (PurchaseOrder.done == False) | (PurchaseOrder.done.is_(None))
        ).order_by(
        PurchaseOrder.purchase_order_number.desc()
        ).all()
       
    vendor_options = sorted(
        {po.vendor.vendor_name for po in purchase_orders}
    )
    
    vendor_name = ""
    vendor_name_error = ""
    detail_ids = ''
    
    if request.method == "POST":
        vendor_name = request.form.get('vendor_name')

        purchase_orders = (
            PurchaseOrder.query
            .filter(
                PurchaseOrder.cancelled.is_(None),
                PurchaseOrder.vendor.has(vendor_name=vendor_name),
                (PurchaseOrder.done == False) | (PurchaseOrder.done.is_(None))
                )
            .order_by(PurchaseOrder.purchase_order_number.desc())
            .all()
        )    

        if request.form.get('cmd_button') == "Create RR":
            detail_ids = request.form.getlist('detail_ids')
            detail_ids = list(map(int, detail_ids))
            detail_ids = [int(x) for x in detail_ids]
            
            if detail_ids:
                count = len(detail_ids)
                if count > 10:
                    vendor_name_error = "Selected items cannot be more than 10."
                else:
                    from_po = {
                        "vendor_name": vendor_name,
                        "detail_ids": detail_ids
                    }
                    return redirect(url_for(f'receiving_report.add', from_po=from_po))
            else:
                vendor_name_error = "Please select an item to receive."

    else:
        purchase_orders = []
   
    
    context = {
        "purchase_orders": purchase_orders,
        "vendor_options": vendor_options,
        "vendor_name": vendor_name,
        "vendor_name_error": vendor_name_error,
        "detail_ids": detail_ids
    }

    return render_template(f"{app_name}/pending.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    raw_material_dropdown = [{"id": raw_material.id, "raw_material_name": raw_material.raw_material_name} for raw_material in RawMaterial.query.order_by('raw_material_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    vendor_dropdown = [{"id": vendor.id, "vendor_name": vendor.vendor_name} for vendor in Vendor.query.order_by('vendor_name').all()]
    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            form.user_prepare_id = current_user.id
            form.save()
            flash(f"{form.purchase_order_number} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        form.purchase_order_number = next_control_number(
            obj=PurchaseOrder, 
            control_number_field="purchase_order_number", 
            record_date=today
            )
        form.currency = "PHP"

        last_entry = (
                        PurchaseOrder.query
                        .join(UserPurchaseOrder)
                        .filter(UserPurchaseOrder.user_id == current_user.id)
                        .order_by(PurchaseOrder.id.desc())
                        .first()
                    )

        if last_entry:
            form.prepared_by = last_entry.prepared_by
            form.requested_by = last_entry.requested_by
            form.checked_by = last_entry.checked_by
            form.approved_by = last_entry.approved_by
        

    context = {
        "form": form,
        "raw_material_dropdown": raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "vendor_dropdown": vendor_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    raw_material_dropdown = [{"id": raw_material.id, "raw_material_name": raw_material.raw_material_name} for raw_material in RawMaterial.query.order_by('raw_material_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    vendor_dropdown = [{"id": vendor.id, "vendor_name": vendor.vendor_name} for vendor in Vendor.query.order_by('vendor_name').all()]

    purchase_order = PurchaseOrder.query.get_or_404(record_id)

    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            cmd_button = request.form.get("cmd_button")
            if cmd_button == "Submit for Printing":
                form.submit()

            form.user_prepare_id = current_user.id
            form.save()

            if cmd_button == "Submit for Printing":
                flash(f"{form.purchase_order_number} has been submitted for printing.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))
            elif cmd_button == "Save Draft":
                flash(f"{form.purchase_order_number} has been updated.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        form.populate(purchase_order)

    context = {
        "form": form,
        "raw_material_dropdown": raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "vendor_dropdown": vendor_dropdown,
        "purchase_order": purchase_order,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    raw_material_dropdown = [{"id": raw_material.id, "raw_material_name": raw_material.raw_material_name} for raw_material in RawMaterial.query.order_by('raw_material_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    vendor_dropdown = [{"id": vendor.id, "vendor_name": vendor.vendor_name} for vendor in Vendor.query.order_by('vendor_name').all()]

    purchase_order = PurchaseOrder.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form.populate(purchase_order)

    context = {
        "form": form,
        "raw_material_dropdown": raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "vendor_dropdown": vendor_dropdown,
        "purchase_order": purchase_order,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("purchase_order.home"))

    obj = PurchaseOrder.query.get_or_404(record_id)
    details = PurchaseOrderDetail.query.filter(PurchaseOrderDetail.purchase_order_id==record_id).all()
    preparer = obj.preparer

    try:
        db.session.delete(preparer)
        for detail in details:
            db.session.delete(detail)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj.purchase_order_number} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/cancel/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(record_id):   
    purchase_order = PurchaseOrder.query.get_or_404(record_id)
    purchase_order.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{purchase_order.purchase_order_number} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/print/<int:record_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(record_id):   
    obj = PurchaseOrder.query.get_or_404(record_id)

    context = {
        "obj": obj,
    }

    try:
        return render_template('purchase_order/print_user_defined.html', **context)
    except TemplateNotFound:
        return render_template('purchase_order/print.html', **context)


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("purchase_order.home"))

    obj = PurchaseOrder.query.get_or_404(record_id)
    obj.submitted = ""
    obj.cancelled = ""

    db.session.commit()
    flash(f"{getattr(obj, f'{app_name}_number')} has been unlocked.", category="success")

    return redirect(url_for(f'{app_name}.edit', record_id=record_id))


@bp.route("/autocomplete", methods=['GET'])
@login_required
def raw_material_description_autocomplete():
    options = list({row.raw_material_description for row in PurchaseOrderDetail.query.order_by(PurchaseOrderDetail.raw_material_description).all()})
    return Response(json.dumps(options), mimetype='application/json')