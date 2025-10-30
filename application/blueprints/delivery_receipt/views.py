from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from dataclasses import dataclass
import datetime
from sqlalchemy.exc import IntegrityError
from .models import DeliveryReceipt as Obj
from .models import DeliveryReceiptDetail as ObjDetail
from .. delivery_receipt_extra.models import DeliveryReceiptExtra
from .forms import Form
from .. product import Product
from .. measure import Measure
from .. customer import Customer
from application.extensions import db, month_first_day, month_last_day, next_control_number 
from .extensions import create_summary
from .. user import login_required, roles_accepted
from . import app_name, app_label


bp = Blueprint(app_name, __name__, template_folder="pages", url_prefix=f"/{app_name}")
ROLES_ACCEPTED = app_label


@bp.route("/delivery_summary", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delivery_summary():
    if request.method == "POST":
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
    else:
        date_from = month_first_day()
        date_to = month_last_day()

    delivery_corp_rows = Obj.query.filter(
        Obj.record_date.between(date_from, date_to)).order_by(
        Obj.record_date.desc(), Obj.id.desc()
        ).all()
        
    delivery_extra_rows = Obj.query.filter(
        Obj.record_date.between(date_from, date_to)).order_by(
        Obj.record_date.desc(), Obj.id.desc()
        ).all()
    
    rows = create_summary(delivery_corp_rows, delivery_extra_rows)

    context = {
        "rows": rows,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/delivery_summary.html", **context)


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
    from .. sales_order import SalesOrderDetail
    
    product_dropdown = [{"id": product.id, "product_name": product.product_name} for product in Product.query.order_by('product_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    customer_dropdown = [{"id": customer.id, "dropdown_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    so_numbers = [sales_order.sales_order_number for sales_order in SalesOrder.query.order_by('sales_order_number').all() if sales_order.is_submitted()]
    
    outstanding_orders = [order.remaining_order_dict() for order in SalesOrderDetail.query.all()]
    
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
        # form.delivery_receipt_number = next_control_number(
        #     obj=Obj, 
        #     control_number_field=f"{app_name}_number"
        #     )
        form.checked_by = "WARLITO FUENTES"
        form.approved_by = "DENNIS M. GALANG"

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,
        "so_numbers": so_numbers,
        "outstanding_orders": outstanding_orders,

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
                return  redirect(url_for(f'{app_name}.edit', record_id=form.id))

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
    details = ObjDetail.query.filter(ObjDetail.delivery_receipt_id==record_id).all()
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
        return redirect(url_for("delivery_receipt.home"))

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
    obj = Obj.query.get_or_404(record_id)

    product_code = getattr(obj, f"{app_name}_details")[0].product.customer_code
    so_number = ", ".join({ row.so_number for row in getattr(obj, f"{app_name}_details") })
    
    context = {
        "obj": obj,
        "product_code": product_code,
        "so_number": so_number,
        "current_app": current_app,
        "delivery_receipt_number_position": delivery_receipt_number_position,
        "customer_name_position": customer_name_position,
        "record_date_position": record_date_position,
        "customer_address_position": customer_address_position,
        "po_number_position": po_number_position,
        "articles_position": articles_position,
        "customer_tin_position": customer_tin_position,
        "customer_business_style_position": customer_business_style_position,
        "so_number_position": so_number_position,
        "vendor_code_position": vendor_code_position,
        "salesman_position": salesman_position,
        "quantity_position": quantity_position,
        "measure_name_position": measure_name_position,
        "product_code_position": product_code_position,
        "product_name_position": product_name_position,
        "notes_position": notes_position,
        "product_code_description_position": product_code_description_position,
        "stacking_position": stacking_position,
        "production_date_position": production_date_position,
        "checked_by_position": checked_by_position,
        "carrier_position": carrier_position,
        "approved_by_position": approved_by_position,
    }

    return render_template(f"{app_name}/print.html", **context)


@dataclass
class Position:
    top: int = None
    left: int = None
    font_size: int = None
    width: int = None
    margin_left: int = None
    margin_right: int = None

top_increment = 1 

delivery_receipt_number_position = Position(top=13 + top_increment, left=185, font_size=13)

customer_name_position = Position(top=39 + top_increment, left=41, font_size=18)
record_date_position = Position(top=40 + top_increment, left=168, font_size=13)

customer_address_position = Position(top=46 + top_increment, left=33, font_size=12)
po_number_position = Position(top=45, left=173 + top_increment, font_size=13)

customer_tin_position = Position(top=51 + top_increment, left=28, font_size=13)
customer_business_style_position = Position(top=51 + top_increment, left=95, font_size=13)
so_number_position = Position(top=51 + top_increment, left=173, font_size=13)

vendor_code_position = Position(top=57 + top_increment, left=36, font_size=13)
salesman_position = Position(top=56 + top_increment, left=178, font_size=13)

articles_position = Position(top=70 + top_increment, left=15)

quantity_position = Position(width=25, font_size=14)
measure_name_position = Position(width=38, font_size=14)
product_code_position = Position(width=20, font_size=14)
product_name_position = Position(width=100, font_size=14)
notes_position = Position(width=100, font_size=14)

product_code_description_position = Position(margin_left=90, font_size=14)
stacking_position = Position(margin_left=85, font_size=14)
production_date_position = Position(margin_left=85, font_size=14)

checked_by_position = Position(top=141 + top_increment, left=15, font_size=13)
carrier_position = Position(top=141 + top_increment, left=65, font_size=13)
approved_by_position = Position(top=141 + top_increment, left=105, font_size=13)
