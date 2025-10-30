from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from dataclasses import dataclass
import datetime
from sqlalchemy.exc import IntegrityError
from .models import DeliveryReceiptExtra as Obj
from .models import DeliveryReceiptExtraDetail as ObjDetail
from .forms import Form
from .. product import Product
from .. measure import Measure
from .. customer import Customer
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

    rows = Obj.query.filter(
        Obj.record_date.between(date_from, date_to)).order_by(
        Obj.record_date.desc(), Obj.id.desc()
        ).all()
        

    context = {
        "rows": rows,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    from .. sales_order import SalesOrder
    product_dropdown = [{"id": product.id, "product_name": product.product_name} for product in Product.query.order_by('product_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    customer_dropdown = [{"id": customer.id, "dropdown_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    so_numbers = [sales_order.sales_order_number for sales_order in SalesOrder.query.order_by('sales_order_number').all() if sales_order.is_submitted()]
    
    
    if request.method == "POST":
        form = Form()
        form._post(request.form)

        if form._validate_on_submit():
            form.user_prepare_id = current_user.id
            form._save()
            flash(f"{getattr(form, f'{app_name}_number')} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        # form.delivery_receipt_extra_number = next_control_number(
        #     obj=Obj, 
        #     control_number_field=f"{app_name}_number"
        #     )
        form.prepared_by = "WARLITO FUENTES"
        form.checked_by = "ARVIE VALLE"
        form.approved_by = "DENNIS M. GALANG"

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,
        "so_numbers": so_numbers,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    from .. sales_order import SalesOrder
    product_dropdown = [{"id": product.id, "product_name": product.product_name} for product in Product.query.order_by('product_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    customer_dropdown = [{"id": customer.id, "dropdown_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    so_numbers = [sales_order.sales_order_number for sales_order in SalesOrder.query.order_by('sales_order_number').all() if sales_order.is_submitted()]
    
    record = Obj.query.get_or_404(record_id)

    if request.method == "POST":
        form = Form()
        form._post(request.form)

        if form._validate_on_submit():
            cmd_button = request.form.get("cmd_button")
            if cmd_button == "Submit for Printing":
                form._submit()

            form.user_prepare_id = current_user.id
            form._save()

            if cmd_button == "Submit for Printing":
                flash(f"{getattr(form, f'{app_name}_number')} has been submitted for printing.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))
            elif cmd_button == "Save Draft":
                flash(f"{getattr(form, f'{app_name}_number')} has been updated.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        form._populate(record)

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,      
        "so_numbers": so_numbers,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    from .. sales_order import SalesOrder
    product_dropdown = [{"id": product.id, "product_name": product.product_name} for product in Product.query.order_by('product_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    customer_dropdown = [{"id": customer.id, "dropdown_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    so_numbers = [sales_order.sales_order_number for sales_order in SalesOrder.query.order_by('sales_order_number').all() if sales_order.is_submitted()]

    record = Obj.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form._populate(record)

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,
        "so_numbers": so_numbers,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for(f"{app_name}.home"))

    obj = Obj.query.get_or_404(record_id)
    details = ObjDetail.query.filter(ObjDetail.delivery_receipt_extra_id==record_id).all()
    preparer = obj.preparer

    try:
        db.session.delete(preparer)
        for detail in details:
            db.session.delete(detail)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{getattr(obj, f'{app_name}_number')} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("delivery_receipt_extra.home"))

    obj = Obj.query.get_or_404(record_id)
    obj.submitted = ""
    obj.cancelled = ""

    db.session.commit()
    flash(f"{getattr(obj, f'{app_name}_number')} has been unlocked.", category="success")

    return redirect(url_for(f'{app_name}.edit', record_id=record_id))


@bp.route("/cancel/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(record_id):   
    obj = Obj.query.get_or_404(record_id)
    obj.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{getattr(obj, f'{app_name}_number')} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/print/<int:record_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(record_id):   
    top_increment = -3
    # top_increment = 0 old warlito setup
    obj = Obj.query.get_or_404(record_id)

    so_number = ", ".join({ row.so_number for row in getattr(obj, f"{app_name}_details") })

    context = {}

    context["obj"] = obj

    context["rows"] = obj.delivery_receipt_extra_details
    context["so_number"] = so_number
    
    context["header_positions"] = [
        ("delivery_receipt_number", Position(left=172, top=9+top_increment, font_size=13)),
        ("customer_name", Position(left=20, top=33+top_increment, font_size=18)),
        ("formatted_record_date_dr", Position(left=149, top=33+top_increment, font_size=13)),
        ("delivery_address", Position(left=26, top=39+top_increment, font_size=11)),
        ("so_number", Position(left=149, top=36+top_increment, font_size=13)),
        ("po_number", Position(left=149, top=40+top_increment, font_size=13)),
        ("truck_number", Position(left=57, top=47+top_increment, font_size=13)),
        ("terms", Position(left=149, top=45+top_increment, font_size=13)),
        ("articles", Position(left=22, top=58+top_increment)),
        ("salesman", Position(left=23, top=118+top_increment)),
        ("prepared_by", Position(left=13, top=129+top_increment)),
        ("checked_by", Position(left=83, top=129+top_increment)),
        ("approved_by", Position(left=143, top=129+top_increment)),
    ]

    context["article_positions"] = [
        ("product_name", Position(font_size=14, width=109)),
        ("formatted_quantity", Position(font_size=14, width=20)),
        ("notes", Position(font_size=14, margin_left=5)),
    ]

    return render_template(f"{app_name}/print.html", **context)


@dataclass
class Position:
    top: int = None
    left: int = None
    font_size: int = None
    width: int = None
    margin_left: int = None
    margin_right: int = None
