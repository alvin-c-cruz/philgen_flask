from flask import Blueprint, render_template, current_app, g
from .. user import login_required


bp = Blueprint('main', __name__, template_folder="pages")


@bp.route("/")
@login_required
def home():
    

    modules = {
        # "customers": Customer,
        # "measures": Measure,
        # "plastic_labels": PlasticLabel,
        # "vendors": Vendor,
        # "departments": Department 
    }

    context = {}
    for module_name, module in modules.items():
        context[module_name] = [record for record in getattr(module, "query").all() if not record.approved]

    return render_template("main/home.html", **context)


@bp.before_app_request
def set_g():
    g.company_name = current_app.config["COMPANY_NAME"]