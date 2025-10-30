app_name = "receiving_report"
app_label = "Receiving Report"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import ReceivingReport, ReceivingReportDetail
