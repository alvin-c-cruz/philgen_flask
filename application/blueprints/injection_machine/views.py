from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, g
import json
from sqlalchemy.exc import IntegrityError
from .models import InjectionMachine as Obj
from .models import UserInjectionMachine as Preparer
from .models import AdminInjectionMachine as Approver
from .forms import Form
from application.extensions import db, month_first_day, month_last_day
from application.blueprints.user import login_required, roles_accepted
from flask_login import current_user

from . import app_name, app_label


bp = Blueprint(app_name, __name__, template_folder="pages", url_prefix=f"/{app_name}")
ROLES_ACCEPTED = app_label


@bp.route("/", methods=["GET", "POST"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def home():

    records = Obj.query.order_by(getattr(Obj, f"{app_name}_name")).all()

    rows = []
    for record in records:
        rows.append(record)


    context = {
        "rows": rows,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    if request.method == "POST":
        form = Form()
        form._post(request.form)
        form.user_prepare_id = current_user.id

        if form._validate_on_submit():
            form._save()
            return redirect(url_for(f'{app_name}.home'))
    else:
        form = Form()

    context = {
        "form": form,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route(f"/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    if request.method == "POST":
        form = Form()
        form._post(request.form)
        form.user_prepare_id = current_user.id

        if form._validate_on_submit():
            form._save()
            return redirect(url_for(f'{app_name}.home'))

    else:
        obj = Obj.query.get(record_id)
        form = Form()
        form._populate(obj)

    context = {
        "form": form,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):   
    obj = Obj.query.get_or_404(record_id)
    preparer = obj.preparer
    try:
        db.session.delete(preparer)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/approve/<int:record_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def approve(record_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        return redirect(url_for("plastic_label.home"))
    
    obj = Obj.query.get_or_404(record_id)

    _dict = {
        f"{app_name}_id": record_id
    }
    approve = Approver(**_dict)
    approve.user_id = current_user.id

    db.session.add(approve)
    db.session.commit()

    flash(f"Approved: {getattr(obj, f'{app_name}_name')}", category="success")
    return redirect(url_for(f'{app_name}.home'))   
    

@bp.route("/activate/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def activate(record_id):   
    obj = Obj.query.get_or_404(record_id)
    obj.active = True    

    db.session.commit()

    flash(f"{obj} has been activated.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/deactivate/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def deactivate(record_id):   
    obj = Obj.query.get_or_404(record_id)
    obj.active = False    

    db.session.commit()

    flash(f"{obj} has been deactivated.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:record_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        redirect(url_for(f'{app_name}.home'))
    
    obj = Obj.query.get_or_404(record_id)

    _dict = {
        f"{app_name}_id": record_id
    }

    approve = Approver.query.filter_by(**_dict).first()
    
    db.session.delete(approve)
    db.session.commit()

    flash(f"Unlocked: {obj}", category="error")
    return redirect(url_for(f'{app_name}.home'))   
    


@bp.route("/_autocomplete", methods=['GET'])
def autocomplete():
    rows = [row for row in Obj.query.order_by(getattr(Obj, f"{app_name}_name")).all()]
    return Response(json.dumps(rows), mimetype='application/json')
