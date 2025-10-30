from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, Response
import json
from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from .models import SalesOrder, SalesOrderDetail
from .forms import Form
from .. product import Product
from .. measure import Measure
from .. customer import Customer
from .. sales_order_customer import SalesOrderCustomer
from application.extensions import db, year_first_day, year_last_day, next_control_number
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
        date_to = year_last_day()

    sales_orders = SalesOrder.query.filter(
        SalesOrder.record_date.between(date_from, date_to)).order_by(
        SalesOrder.record_date.desc(), SalesOrder.id.desc()
        ).all()
        

    context = {
        "sales_orders": sales_orders,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/schedule", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def schedule():     
    orders = SalesOrderDetail.query.order_by(SalesOrderDetail.delivery_date).all()

    context = {
        "orders": orders,
    }

    return render_template(f"{app_name}/schedule.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    product_dropdown = [{"id": product.id, "product_name": f"{product.inhouse_name} ({product.product_name})"} for product in Product.query.order_by('inhouse_name').all() if product.active]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    sales_order_customer_dropdown = [{"id": customer.id, "customer_name": customer.customer_name} for customer in SalesOrderCustomer.query.order_by('customer_name').all()]
    customer_dropdown = [{"id": customer.id, "customer_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            form.user_prepare_id = current_user.id
            form.save()
            flash(f"{form.sales_order_number} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', sales_order_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        form.sales_order_number = next_control_number(
            obj=SalesOrder, 
            control_number_field="sales_order_number", 
            record_date=today
            )

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,
        "sales_order_customer_dropdown": sales_order_customer_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:sales_order_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(sales_order_id):   
    product_dropdown = [{"id": product.id, "product_name": f"{product.inhouse_name} ({product.product_name})"} for product in Product.query.order_by('inhouse_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    customer_dropdown = [{"id": customer.id, "customer_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    sales_order_customer_dropdown = [{"id": customer.id, "customer_name": customer.customer_name} for customer in SalesOrderCustomer.query.order_by('customer_name').all()]

    sales_order = SalesOrder.query.get_or_404(sales_order_id)

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
                flash(f"{form.sales_order_number} has been submitted for printing.", category="success")
                return redirect(url_for(f'{app_name}.edit', sales_order_id=form.id))
            elif cmd_button == "Save Draft":
                flash(f"{form.sales_order_number} has been updated.", category="success")
                return redirect(url_for(f'{app_name}.edit', sales_order_id=form.id))

    else:
        form = Form()
        form.populate(sales_order)

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,
        "sales_order": sales_order,       
        "sales_order_customer_dropdown": sales_order_customer_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:sales_order_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(sales_order_id):   
    product_dropdown = [{"id": product.id, "product_name": f"{product.inhouse_name} ({product.product_name})"} for product in Product.query.order_by('inhouse_name').all()]
    measure_dropdown = [{"id": measure.id, "measure_name": measure.measure_name} for measure in Measure.query.order_by('measure_name').all()]
    customer_dropdown = [{"id": customer.id, "customer_name": customer.customer_name} for customer in Customer.query.order_by('customer_name').all()]
    sales_order_customer_dropdown = [{"id": customer.id, "customer_name": customer.customer_name} for customer in SalesOrderCustomer.query.order_by('customer_name').all()]

    sales_order = SalesOrder.query.get_or_404(sales_order_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form.populate(sales_order)

    context = {
        "form": form,
        "product_dropdown": product_dropdown,
        "measure_dropdown": measure_dropdown,
        "customer_dropdown": customer_dropdown,
        "sales_order": sales_order,       
        "sales_order_customer_dropdown": sales_order_customer_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:sales_order_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(sales_order_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("sales_order.home"))

    obj = SalesOrder.query.get_or_404(sales_order_id)
    details = SalesOrderDetail.query.filter(SalesOrderDetail.sales_order_id==sales_order_id).all()
    preparer = obj.preparer

    try:
        db.session.delete(preparer)
        for detail in details:
            db.session.delete(detail)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj.sales_order_number} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/cancel/<int:sales_order_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(sales_order_id):   
    sales_order = SalesOrder.query.get_or_404(sales_order_id)
    sales_order.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{sales_order.sales_order_number} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:sales_order_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(sales_order_id):   
    sales_order = SalesOrder.query.get_or_404(sales_order_id)
    sales_order.submitted = ""
    sales_order.cancelled = ""
    db.session.commit()
    flash(f"{sales_order.sales_order_number} has been unlocked.", category="success")

    return redirect(url_for(f'{app_name}.edit', sales_order_id=sales_order_id))


@bp.route("/print/<int:sales_order_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(sales_order_id):   
    sales_order = SalesOrder.query.get_or_404(sales_order_id)

    context = {
        "sales_order": sales_order,
        "current_app": current_app
    }

    return render_template(f"{app_name}/print.html", **context)


@bp.route("/get_outstanding_orders")
@login_required
def get_outstanding_orders():
    customer_id = request.args.get('customer_id', None)

    print(customer_id)

    # Gather outstanding orders
    orders = SalesOrderDetail.query.filter_by(customer_id=customer_id).all()

    # Convert orders to a list of dictionaries
    orders_list = [order.remaining_order_dict() for order in orders]

    return Response(json.dumps(orders_list), mimetype='application/json')