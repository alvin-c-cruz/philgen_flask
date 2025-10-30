from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from .models import PurchaseRequest, PurchaseRequestDetail
from .forms import Form
from .. raw_material import RawMaterial
from .. measure import Measure
from .. department import Department
from application.extensions import db, month_first_day, month_last_day, next_control_number
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
        date_from = month_first_day()
        date_to = month_last_day()

    purchase_requests = PurchaseRequest.query.filter(
        PurchaseRequest.record_date.between(date_from, date_to)).order_by(
        PurchaseRequest.record_date.desc(), PurchaseRequest.id.desc()
        ).all()
        

    context = {
        "purchase_requests": purchase_requests,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    raw_material_dropdown = [{"id": raw_material.id, "raw_material_name": raw_material.raw_material_name} for raw_material in RawMaterial.query.order_by('raw_material_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    department_dropdown = [{"id": department.id, "department_name": department.department_name} for department in Department.query.order_by('department_name').all()]
    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            form.user_prepare_id = current_user.id
            form.save()
            flash(f"{form.purchase_request_number} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', purchase_request_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        form.purchase_request_number = next_control_number(
            obj=PurchaseRequest, 
            control_number_field="purchase_request_number", 
            record_date=today
            )
        
        if current_user.user_name == "ARVIE":            
            form.prepared_by="ARVIE VALLE"
        else:
            form.prepared_by="JOSIE LO"
            
        form.checked_by="DENNIS M. GALANG"
        form.approved_by="IRWIN C. ONG"

    context = {
        "form": form,
        "raw_material_dropdown": raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "department_dropdown": department_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:purchase_request_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(purchase_request_id):   
    raw_material_dropdown = [{"id": raw_material.id, "raw_material_name": raw_material.raw_material_name} for raw_material in RawMaterial.query.order_by('raw_material_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    department_dropdown = [{"id": department.id, "department_name": department.department_name} for department in Department.query.order_by('department_name').all()]

    purchase_request = PurchaseRequest.query.get_or_404(purchase_request_id)

    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            cmd_button = request.form.get("cmd_button")
            if cmd_button == "Submit for PO":
                form.submit()

            form.user_prepare_id = current_user.id
            form.save()

            if cmd_button == "Submit for PO":
                flash(f"{form.purchase_request_number} has been submitted to purchasing department.", category="success")
                return redirect(url_for(f'{app_name}.edit', purchase_request_id=form.id))
            elif cmd_button == "Save Draft":
                flash(f"{form.purchase_request_number} has been updated.", category="success")
                return  redirect(url_for('purchase_request.home'))

    else:
        form = Form()
        form.populate(purchase_request)

    context = {
        "form": form,
        "raw_material_dropdown": raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "department_dropdown": department_dropdown,
        "purchase_request": purchase_request,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:purchase_request_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(purchase_request_id):   
    raw_material_dropdown = [{"id": raw_material.id, "raw_material_name": raw_material.raw_material_name} for raw_material in RawMaterial.query.order_by('raw_material_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    department_dropdown = [{"id": department.id, "department_name": department.department_name} for department in Department.query.order_by('department_name').all()]

    purchase_request = PurchaseRequest.query.get_or_404(purchase_request_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form.populate(purchase_request)

    context = {
        "form": form,
        "raw_material_dropdown": raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "department_dropdown": department_dropdown,
        "purchase_request": purchase_request,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:purchase_request_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(purchase_request_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("purchase_request.home"))

    obj = PurchaseRequest.query.get_or_404(purchase_request_id)
    details = PurchaseRequestDetail.query.filter(PurchaseRequestDetail.purchase_request_id==purchase_request_id).all()
    preparer = obj.preparer

    try:
        db.session.delete(preparer)
        for detail in details:
            db.session.delete(detail)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj.purchase_request_number} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/cancel/<int:purchase_request_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(purchase_request_id):   
    purchase_request = PurchaseRequest.query.get_or_404(purchase_request_id)
    purchase_request.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{purchase_request.purchase_request_number} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/print/<int:purchase_request_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(purchase_request_id):   
    purchase_request = PurchaseRequest.query.get_or_404(purchase_request_id)

    context = {
        "purchase_request": purchase_request,
    }

    return render_template(f"{app_name}/print.html", **context)


@bp.route("/pending", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def pending():
    rows = PurchaseRequest.query.filter(
        PurchaseRequest.cancelled.is_(None),
        PurchaseRequest.done.is_(None),
        ).order_by(
        PurchaseRequest.purchase_request_number.desc()
        ).all()

    context = {
        "rows": rows,
    }

    return render_template(f"{app_name}/pending.html", **context)


@bp.route("/done/<int:record_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def done(record_id):   
    obj = PurchaseRequest.query.get_or_404(record_id)
    obj.done = str(datetime.datetime.today())[:10]
    db.session.commit()

    return redirect(url_for('purchase_request.pending'))


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for(f"{app_name}.home"))

    obj = PurchaseRequest.query.get_or_404(record_id)
    obj.submitted = ""
    obj.cancelled = ""

    db.session.commit()
    flash(f"{getattr(obj, f'{app_name}_number')} has been unlocked.", category="success")

    return redirect(url_for(f'{app_name}.edit', purchase_request_id=record_id))


