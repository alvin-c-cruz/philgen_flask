app_name = "plastic_label_receipt"
app_label = "Plastic Label Receiving Report"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticLabelReceipt, PlasticLabelReceiptDetail
