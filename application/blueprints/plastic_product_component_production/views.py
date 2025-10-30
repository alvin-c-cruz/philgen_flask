from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
import datetime
from sqlalchemy.exc import IntegrityError
from .models import PlasticProductComponentProduction
from .models import PlasticProductComponentProductionDetail
from .forms import Form
from .. plastic_product_component import PlasticProductComponent
from .. plastic_product_component_status import PlasticProductComponentStatus
from .. measure import Measure
from .. shift import Shift
from .. injection_machine import InjectionMachine
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

    plastic_product_component_productions = PlasticProductComponentProduction.query.filter(
        PlasticProductComponentProduction.record_date.between(date_from, date_to)).order_by(
        PlasticProductComponentProduction.record_date.desc(), PlasticProductComponentProduction.id.desc()
        ).all()
        

    context = {
        "plastic_product_component_productions": plastic_product_component_productions,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    plastic_product_component_dropdown = [{"id": record.id, "dropdown_name": f"{record.plastic_product_component_name} ({record.plastic_product_component_code})"} for record in PlasticProductComponent.query.order_by('plastic_product_component_name').all() if record.active]
    measure_dropdown = [{"id": record.id, "dropdown_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]
    shift_dropdown = [{"id": record.id, "dropdown_name": record.shift_name} for record in Shift.query.order_by('shift_name').all()]   
    injection_machine_dropdown = [{"id": record.id, "dropdown_name": record.injection_machine_name} for record in InjectionMachine.query.order_by('injection_machine_name').all() if record.active]
    plastic_product_component_status_dropdown = [{"id": record.id, "dropdown_name": record.plastic_product_component_status_name} for record in PlasticProductComponentStatus.query.order_by('plastic_product_component_status_name').all() if record.active]

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
                obj=PlasticProductComponentProduction, 
                control_number_field=f"{app_name}_number"
                )
            )

    context = {
        "form": form,
        "plastic_product_component_dropdown": plastic_product_component_dropdown,
        "measure_dropdown": measure_dropdown,
        "shift_dropdown": shift_dropdown,
        "injection_machine_dropdown": injection_machine_dropdown,
        "plastic_product_component_status_dropdown": plastic_product_component_status_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    plastic_product_component_dropdown = [{"id": record.id, "dropdown_name": f"{record.plastic_product_component_name} ({record.plastic_product_component_code})"} for record in PlasticProductComponent.query.order_by('plastic_product_component_name').all() if record.active]
    measure_dropdown = [{"id": record.id, "dropdown_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]
    shift_dropdown = [{"id": record.id, "dropdown_name": record.shift_name} for record in Shift.query.order_by('shift_name').all()]   
    injection_machine_dropdown = [{"id": record.id, "dropdown_name": record.injection_machine_name} for record in InjectionMachine.query.order_by('injection_machine_name').all() if record.active]
    plastic_product_component_status_dropdown = [{"id": record.id, "dropdown_name": record.plastic_product_component_status_name} for record in PlasticProductComponentStatus.query.order_by('plastic_product_component_status_name').all() if record.active]

    record = PlasticProductComponentProduction.query.get_or_404(record_id)

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
                return  redirect(url_for(f'{app_name}.home'))

    else:
        form = Form()
        form._populate(record)

    context = {
        "form": form,
        "plastic_product_component_dropdown": plastic_product_component_dropdown,
        "measure_dropdown": measure_dropdown,
        "shift_dropdown": shift_dropdown,
        "injection_machine_dropdown": injection_machine_dropdown,
        "plastic_product_component_status_dropdown": plastic_product_component_status_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    plastic_product_component_dropdown = [{"id": record.id, "dropdown_name": f"{record.plastic_product_component_name} ({record.plastic_product_component_code})"} for record in PlasticProductComponent.query.order_by('plastic_product_component_name').all() if record.active]
    measure_dropdown = [{"id": record.id, "dropdown_name": record.measure_name} for record in Measure.query.order_by('measure_name').all()]
    shift_dropdown = [{"id": record.id, "dropdown_name": record.shift_name} for record in Shift.query.order_by('shift_name').all()]   
    injection_machine_dropdown = [{"id": record.id, "dropdown_name": record.injection_machine_name} for record in InjectionMachine.query.order_by('injection_machine_name').all() if record.active]
    plastic_product_component_status_dropdown = [{"id": record.id, "dropdown_name": record.plastic_product_component_status_name} for record in PlasticProductComponentStatus.query.order_by('plastic_product_component_status_name').all() if record.active]

    record = PlasticProductComponentProduction.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form._populate(record)

    context = {
        "form": form,
        "plastic_product_component_dropdown": plastic_product_component_dropdown,
        "measure_dropdown": measure_dropdown,
        "shift_dropdown": shift_dropdown,
        "injection_machine_dropdown": injection_machine_dropdown,
        "plastic_product_component_status_dropdown": plastic_product_component_status_dropdown,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for(f"{app_name}.home"))

    obj = PlasticProductComponentProduction.query.get_or_404(record_id)
    details = PlasticProductComponentProductionDetail.query.filter(
        getattr(PlasticProductComponentProductionDetail, f"{app_name}_id")==record_id
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
    record = PlasticProductComponentProduction.query.get_or_404(record_id)
    record.cancelled = str(datetime.datetime.today())[:10]
    db.session.commit()
    flash(f"{getattr(record, f'{app_name}_number')} has been cancelled.", category="success")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if current_user.admin:   
        record = PlasticProductComponentProduction.query.get_or_404(record_id)
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
    record = PlasticProductComponentProduction.query.get_or_404(record_id)

    context = {
        "record": record,
        "current_app": current_app
    }

    return render_template(f"{app_name}/print.html", **context)
