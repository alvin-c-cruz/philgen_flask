from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from .models import LithographyReceipt
from .forms import Form
from .. lithography import Lithography
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

    lithography_receipts = LithographyReceipt.query.filter(
        LithographyReceipt.record_date.between(date_from, date_to)).order_by(
        LithographyReceipt.lithography_receipt_number.desc(), LithographyReceipt.id.desc()
        ).all()
        

    context = {
        "lithography_receipts": lithography_receipts,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    lithography_dropdown = [{"id": record.id, "dropdown_name": record.lithography_name} for record in Lithography.query.order_by('lithography_name').all() if record.active]

    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            form.user_prepare_id = current_user.id
            form.save()
            flash(f"{form.lithography_receipt_number} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        form.lithography_receipt_number = next_control_number(
            obj=LithographyReceipt, 
            control_number_field="lithography_receipt_number"
            )

    context = {
        "form": form,
        "lithography_dropdown": lithography_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    lithography_dropdown = [{"id": record.id, "dropdown_name": record.lithography_name} for record in Lithography.query.order_by('lithography_name').all() if record.active]

    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            cmd_button = request.form.get("cmd_button")             
            form.user_prepare_id = current_user.id
            if cmd_button == "Approve":
                form.submit()
                flash(f"{form.lithography_receipt_number} has been locked.", category="success")
            elif cmd_button == "Save Draft":            
                flash(f"{form.lithography_receipt_number} has been updated.", category="success")
            form.save()
            return  redirect(url_for(f'{app_name}.home'))

    else:
        lithography_receipt = LithographyReceipt.query.get_or_404(record_id)
        form = Form()
        form.populate(lithography_receipt)

    context = {
        "form": form,
        "lithography_dropdown": lithography_dropdown,   
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    lithography_dropdown = [{"id": record.id, "dropdown_name": record.lithography_name} for record in Lithography.query.order_by('lithography_name').all() if record.active]

    lithography_receipt = LithographyReceipt.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form.populate(lithography_receipt)

    context = {
        "form": form,
        "lithography_dropdown": lithography_dropdown,
        "lithography_receipt": lithography_receipt,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for(f"{app_name}.home"))

    obj = LithographyReceipt.query.get_or_404(record_id)
    preparer = obj.preparer

    try:
        db.session.delete(preparer)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj.lithography_receipt_number} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/cancel/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(record_id):   
    lithography_receipt = Lithography.query.get_or_404(record_id)
    lithography_receipt.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{lithography_receipt.lithography_receipt_number} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/lock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def lock(record_id):
    context = {}
    if current_user.admin:   
        lithography_receipt = LithographyReceipt.query.get_or_404(record_id)
        lithography_receipt.submitted = str(datetime.datetime.today())[:10]
        db.session.commit()
        context["date_from"] = request.args.get('date_from')
        context["date_to"] = request.args.get('date_to')

        flash(f"{lithography_receipt.lithography_receipt_number} has been locked.", category="success")
    else:
        flash(f"Administrator right is needed for this function.", category="error")

    return redirect(url_for(f'{app_name}.home'), **context)

@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if current_user.admin:   
        lithography_receipt = LithographyReceipt.query.get_or_404(record_id)
        lithography_receipt.submitted = ""
        lithography_receipt.cancelled = ""
        db.session.commit()
        flash(f"{lithography_receipt.lithography_receipt_number} has been unlocked.", category="success")
    else:
        flash(f"Administrator right is needed for this function.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/print/<int:record_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(record_id):   
    lithography_receipt = LithographyReceipt.query.get_or_404(record_id)

    context = {
        "lithography_receipt": lithography_receipt,
        "current_app": current_app
    }

    return render_template(f"{app_name}/print.html", **context)
