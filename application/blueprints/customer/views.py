from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import json
from sqlalchemy.exc import IntegrityError
from .models import Customer as Obj
from .models import UserCustomer as Preparer
from .models import AdminCustomer as Approver
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
    rows = Obj.query.order_by(Obj.customer_name).all()

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


@bp.route(f"/edit/<int:customer_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(customer_id):   
    if request.method == "POST":
        form = Form()
        form.post(request.form)
        form.user_prepare_id = current_user.id

        if form.validate_on_submit():
            form.save()
            return redirect(url_for(f'{app_name}.home'))

    else:
        obj = Obj.query.get(customer_id)
        form = Form()
        form.populate(obj)

    context = {
        "form": form,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:customer_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(customer_id):   
    obj = Obj.query.get_or_404(customer_id)
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


@bp.route("/approve/<int:customer_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def approve(customer_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        return redirect(url_for("customer.home"))
    
    obj = Obj.query.get_or_404(customer_id)

    approve = Approver(
        customer_id=customer_id,
        user_id=current_user.id
    )

    db.session.add(approve)
    db.session.commit()

    flash(f"Approved: {obj.customer_name}", category="success")
    return redirect(url_for("customer.home"))   
    

@bp.route("/unlock/<int:customer_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(customer_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        return redirect(url_for("customer.home"))
    
    obj = Obj.query.get_or_404(customer_id)

    approve = Approver.query.filter_by(customer_id=customer_id).first()
    
    db.session.delete(approve)
    db.session.commit()

    flash(f"Unlocked: {obj.customer_name}", category="error")
    return redirect(url_for("customer.home"))   
    

@bp.route("/autocomplete", methods=['GET'])
@login_required
def _autocomplete():
    options = [customer.customer_name for customer in Obj.query.order_by(Obj.customer_name).all()]
    return Response(json.dumps(options), mimetype='application/json')
