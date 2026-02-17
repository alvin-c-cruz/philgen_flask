app_name = "job_order"
app_label = "Job Order"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import JobOrder, JobOrderDetail
