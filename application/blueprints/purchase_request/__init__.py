app_name = "purchase_request"
app_label = "Purchase Request"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PurchaseRequest, PurchaseRequestDetail
