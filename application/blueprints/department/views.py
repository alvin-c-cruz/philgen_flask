from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import json
from sqlalchemy.exc import IntegrityError
from .models import Department as Obj
from .models import UserDepartment as Preparer
from .models import AdminDepartment as Approver
from .forms import Form
from application.extensions import db
from application.blueprints.user import login_required, roles_accepted
from flask_login import current_user

from . import app_name, app_label


bp = Blueprint(app_name, __name__, template_folder="pages", url_prefix=f"/{app_name}")
ROLES_ACCEPTED = app_label


@bp.route("/")
@login_required
@roles_accepted([ROLES_ACCEPTED])
def home():
    rows = Obj.query.order_by(Obj.department_name).all()

    context = {
        "rows": rows
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    if request.method == "POST":
        form = Form()
        form.post(request.form)
        form.user_prepare_id = current_user.id

        if form.validate_on_submit():
            form.save()
            return redirect(url_for(f'{app_name}.home'))
    else:
        form = Form()

    context = {
        "form": form,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route(f"/edit/<int:department_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(department_id):   
    if request.method == "POST":
        form = Form()
        form.post(request.form)
        form.user_prepare_id = current_user.id

        if form.validate_on_submit():
            form.save()
            return redirect(url_for(f'{app_name}.home'))

    else:
        obj = Obj.query.get(department_id)
        form = Form()
        form.populate(obj)

    context = {
        "form": form,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:department_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(department_id):   
    obj = Obj.query.get_or_404(department_id)
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


@bp.route("/approve/<int:department_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def approve(department_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        return redirect(url_for("department.home"))
    
    obj = Obj.query.get_or_404(department_id)

    approve = Approver(
        department_id=department_id,
        user_id=current_user.id
    )

    db.session.add(approve)
    db.session.commit()

    flash(f"Approved: {obj.department_name}", category="success")
    return redirect(url_for("department.home"))   
    


@bp.route("/_autocomplete", methods=['GET'])
def autocomplete():
    rows = [row for row in Obj.query.order_by(Obj.department_name).all()]
    return Response(json.dumps(rows), mimetype='application/json')
