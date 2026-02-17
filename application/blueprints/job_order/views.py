from flask import Blueprint, request, render_template, redirect, url_for, flash, Response
from flask_login import current_user
import datetime
import json
from sqlalchemy.exc import IntegrityError
from jinja2 import TemplateNotFound

from . import app_name, app_label
from .. user import login_required, roles_accepted

from application.extensions import db, year_first_day, year_last_day, next_control_number

from .models import JobOrder as Obj, JobOrderDetail as ObjDetail
from .forms import Form


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

    rows = Obj.query.filter(
        Obj.record_date.between(date_from, date_to)
        ).order_by(
        getattr(Obj, f"{app_name}_number").desc()
        ).all()
        

    context = {
        "app_label": app_label,
        "rows": rows,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    if request.method == "POST":
        form = Form()
        form.post(request.form)

        if form.validate_on_submit():
            form.user_prepare_id = current_user.id
            form.save()
            flash(f"{getattr(form,f'{app_name}_number')} has been added.", category="success")
            return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        today = str(datetime.date.today())[:10]
        form.record_date = today
        next_number = next_control_number(
            obj=Obj, 
            control_number_field=f'{app_name}_number', 
            record_date=today
            )
        setattr(form,f'{app_name}_number',next_number)

        last_entry = Obj.query.order_by(Obj.id.desc()).first()

        if last_entry:
            form.prepared_by = last_entry.prepared_by
            form.checked_by = last_entry.checked_by
            form.approved_by = last_entry.approved_by
        

    context = {
        "app_label": app_label,
        "form": form,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/pending", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def pending():
    rows = Obj.query.filter(
        Obj.submitted,
        Obj.cancelled.is_(None),
        (Obj.done == False) | (Obj.done.is_(None))
        ).order_by(
        getattr(Obj, f'{app_name}_number').desc()
        ).all()
       
    customer_options = sorted(
        {i.customer.customer_name for i in rows}
    )
    
    customer_name = ""
    customer_name_error = ""
    detail_ids = ''
    
    if request.method == "POST":
        customer_name = request.form.get('customer_name')

        if customer_name:
            rows = (
                Obj.query
                .filter(
                    Obj.customer.has(customer_name=customer_name),
                    Obj.submitted,
                    Obj.cancelled.is_(None),
                    (Obj.done == False) | (Obj.done.is_(None))
                    )
                .order_by(getattr(Obj, f'{app_name}_number').desc())
                .all()
            )    
        else:
            rows = (
                Obj.query
                .filter(
                    Obj.submitted,
                    Obj.cancelled.is_(None),
                    (Obj.done == False) | (Obj.done.is_(None))
                    )
                .order_by(
                    getattr(Obj, f'{app_name}_number').desc()
                    )
                .all()
            )    


        def goto_DR(cmd_button):
            detail_ids = request.form.getlist('detail_ids')
            detail_ids = list(map(int, detail_ids))
            detail_ids = [int(x) for x in detail_ids]
            _error = None
            
            if detail_ids:
                count = len(detail_ids)
                if count > 10:
                    _error = "Selected items cannot be more than 10."
                else:
                    from_po = {
                        "customer_name": customer_name,
                        "detail_ids": detail_ids
                    }
                    return redirect(url_for('delivery_receipt.add' if cmd_button=="Create DR" else 'delivery_receipt_extra.add', from_po=from_po))
            else:
                _error = "Please select an item to deliver."
            return _error

        if request.form.get('cmd_button') == "Create DR":
            customer_name_error = goto_DR("Create DR")
            
        if request.form.get('cmd_button') == "Create ARD":
            customer_name_error = goto_DR("Create ARD")
   
    
    context = {
        "rows": rows,
        "customer_options": customer_options,
        "customer_name": customer_name,
        "customer_name_error": customer_name_error,
        "detail_ids": detail_ids
    }

    return render_template(f"{app_name}/pending.html", **context)

@bp.route("/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    obj = Obj.query.get_or_404(record_id)

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
                flash(f"{getattr(form, f'{app_name}_number')} has been submitted for printing.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))
            elif cmd_button == "Save Draft":
                flash(f"{getattr(form, f'{app_name}_number')} has been updated.", category="success")
                return redirect(url_for(f'{app_name}.edit', record_id=form.id))

    else:
        form = Form()
        form.populate(obj)

    context = {
        "form": form,
        "obj": obj,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/view/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def view(record_id):   
    obj = Obj.query.get_or_404(record_id)

    if request.method == "POST":
        flash("Record is locked for editting. Contact your administrator.", category="error")

    form = Form()
    form.populate(obj)

    context = {
        "form": form,
        "obj": obj,       
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("purchase_order.home"))

    obj = Obj.query.get_or_404(record_id)
    details = ObjDetail.query.filter(ObjDetail.job_order_id==record_id).all()
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

    context = {
        "obj": obj,
    }

    return render_template(f'{app_name}/print.html', **context)


@bp.route("/unlock/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if not current_user.admin:
        flash("Administrator rights is required to conduct this activity.", category="error")
        return redirect(url_for("purchase_order.home"))

    obj = Obj.query.get_or_404(record_id)
    obj.submitted = ""
    obj.cancelled = ""

    db.session.commit()
    flash(f"{getattr(obj, f'{app_name}_number')} has been unlocked.", category="success")

    return redirect(url_for(f'{app_name}.edit', record_id=record_id))

@bp.route("/autocomplete", methods=['GET'])
@login_required
def product_description_autocomplete():
    options = list({row.product_description for row in ObjDetail.query.order_by(ObjDetail.product_description).all()})
    return Response(json.dumps(options), mimetype='application/json')