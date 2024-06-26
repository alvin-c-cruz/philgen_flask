from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from .models import PurchaseOrder as Obj
from .models import  PurchaseOrderDetail as ObjDetail
from .forms import Form
from .. vendor import Vendor
from .. measure import Measure
from application.extensions import db, month_first_day, month_last_day, next_control_number, Url
from .. user import login_required, roles_accepted
from . import app_name, app_label


bp = Blueprint(app_name, __name__, template_folder="pages", url_prefix=f"/{app_name}")
ROLES_ACCEPTED = app_label

url = ""

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
        "url": Url
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    measure_dropdown = [{"id": record.id, "dropdown_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]

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
        setattr(
            form, 
            f"{app_name}_number", 
            next_control_number(
                obj=Obj, 
                control_number_field=f"{app_name}_number"
                )
            )

    context = {
        "form": form,
        "vendor_options": Vendor().options(),
        "measure_dropdown": measure_dropdown,
        "url": Url(Obj),
        "descriptions": [ description for description in {obj.description for obj in ObjDetail.query.order_by('description').all()}  ]
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    measure_dropdown = [{"id": record.id, "dropdown_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]

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
                return redirect(url_for(f'{app_name}.edit', record_id=record_id))
            elif cmd_button == "Save Draft":
                flash(f"{getattr(form, f'{app_name}_number')} has been updated.", category="success")
                return  redirect(url_for(f'{app_name}.home'))

    else:
        form = Form()
        form._populate(record)

    context = {
        "form": form,
        "vendor_options": Vendor().options(),
        "measure_dropdown": measure_dropdown,
        "url": Url(record),
        "descriptions": [ description for description in {obj.description for obj in ObjDetail.query.order_by('description').all()}  ]
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    measure_dropdown = [{"id": record.id, "dropdown_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]

    record = Obj.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form._populate(record)

    context = {
        "form": form,
        "vendor_options": Vendor().options(),
        "measure_dropdown": measure_dropdown,
        "url": Url(record),
        "descriptions": [ description for description in {obj.description for obj in ObjDetail.query.order_by('description').all()}  ]
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

    if obj.submitted or obj.cancelled:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for(f"{app_name}.home"))

    details = ObjDetail.query.filter(
        getattr(ObjDetail, f"{app_name}_id")==record_id
        ).all()
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


@bp.route("/cancel/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(record_id):   
    record = Obj.query.get_or_404(record_id)
    record.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{getattr(record, f'{app_name}_number')} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if current_user.admin:   
        record = Obj.query.get_or_404(record_id)
        record.submitted = ""
        record.cancelled = ""
        db.session.commit()
        flash(f"{getattr(record, f'{app_name}_number')} has been unlocked.", category="success")
    else:
        flash(f"Administrator right is needed for this function.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/print/<int:record_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(record_id):   
    flash("Printing not yet activated.", category="error")
    return redirect(url_for(f"{app_name}.home"))

    record = Obj.query.get_or_404(record_id)

    context = {
        "record": record,
        "current_app": current_app
    }

    return render_template(f"{app_name}/print.html", **context)
