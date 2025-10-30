from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from .models import PlasticRawMaterialAdjustment, PlasticRawMaterialAdjustmentDetail
from .forms import Form
from .. plastic_raw_material import PlasticRawMaterial
from ... measure import Measure
from application.extensions import db, month_first_day, month_last_day, next_control_number
from ... user import login_required, roles_accepted
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

    records = PlasticRawMaterialAdjustment.query.filter(
        PlasticRawMaterialAdjustment.record_date.between(date_from, date_to)).order_by(
        PlasticRawMaterialAdjustment.record_date.desc(), PlasticRawMaterialAdjustment.id.desc()
        ).all()
        

    context = {
        "records": records,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    plastic_raw_material_dropdown = [{"id": record.id, "plastic_raw_material_name": f"{record.plastic_raw_material_name} ({record.plastic_raw_material_code})"} for record in PlasticRawMaterial.query.order_by('plastic_raw_material_name').all() if record.active]
    measure_dropdown = [{"id": record.id, "measure_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]
    
    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            form.user_prepare_id = current_user.id
            form.save()
            flash(f"{form.plastic_raw_material_adjustment_number} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        form.plastic_raw_material_adjustment_number = next_control_number(
            obj=PlasticRawMaterialAdjustment, 
            control_number_field="plastic_raw_material_adjustment_number"
            )

    context = {
        "form": form,
        "plastic_raw_material_dropdown": plastic_raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    plastic_raw_material_dropdown = [{"id": record.id, "plastic_raw_material_name": f"{record.plastic_raw_material_name} ({record.plastic_raw_material_code})"} for record in PlasticRawMaterial.query.order_by('plastic_raw_material_name').all() if record.active]
    measure_dropdown = [{"id": record.id, "measure_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]
    
    plastic_raw_material_adjustment = PlasticRawMaterialAdjustment.query.get_or_404(record_id)

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
                flash(f"{form.plastic_raw_material_adjustment_number} has been submitted for printing.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))
            elif cmd_button == "Save Draft":
                flash(f"{form.plastic_raw_material_adjustment_number} has been updated.", category="success")
                return  redirect(url_for(f'{app_name}.home'))

    else:
        form = Form()
        form.populate(plastic_raw_material_adjustment)

    context = {
        "form": form,
        "plastic_raw_material_dropdown": plastic_raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "plastic_raw_material_adjustment": plastic_raw_material_adjustment,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    plastic_raw_material_dropdown = [{"id": record.id, "plastic_raw_material_name": f"{record.plastic_raw_material_name} ({record.plastic_raw_material_code})"} for record in PlasticRawMaterial.query.order_by('plastic_raw_material_name').all() if record.active]
    measure_dropdown = [{"id": record.id, "measure_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]

    plastic_raw_material_adjustment = PlasticRawMaterialAdjustment.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form.populate(plastic_raw_material_adjustment)

    context = {
        "form": form,
        "plastic_raw_material_dropdown": plastic_raw_material_dropdown,
        "measure_dropdown": measure_dropdown,
        "plastic_raw_material_adjustment": plastic_raw_material_adjustment,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for(f"{app_name}.home"))

    obj = PlasticRawMaterialAdjustment.query.get_or_404(record_id)
    details = PlasticRawMaterialAdjustmentDetail.query.filter(PlasticRawMaterialAdjustmentDetail.plastic_raw_material_adjustment_id==record_id).all()
    preparer = obj.preparer

    try:
        db.session.delete(preparer)
        for detail in details:
            db.session.delete(detail)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj.plastic_raw_material_adjustment_number} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/cancel/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def cancel(record_id):   
    plastic_raw_material_adjustment = PlasticRawMaterialAdjustment.query.get_or_404(record_id)
    plastic_raw_material_adjustment.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{plastic_raw_material_adjustment.plastic_raw_material_adjustment_number} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if current_user.admin:   
        plastic_raw_material_adjustment = PlasticRawMaterialAdjustment.query.get_or_404(record_id)
        plastic_raw_material_adjustment.submitted = ""
        plastic_raw_material_adjustment.cancelled = ""
        db.session.commit()
        flash(f"{plastic_raw_material_adjustment.plastic_raw_material_adjustment_number} has been unlocked.", category="success")
    else:
        flash(f"Administrator right is needed for this function.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/print/<int:record_id>", methods=["GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def print(record_id):   
    plastic_raw_material_adjustment = PlasticRawMaterialAdjustment.query.get_or_404(record_id)

    context = {
        "plastic_raw_material_adjustment": plastic_raw_material_adjustment,
        "current_app": current_app
    }

    return render_template(f"{app_name}/print.html", **context)
