app_name = "purchase_order"
app_label = "Purchase Order"
menu_label = (app_name, f"/{app_name}", app_label)
model_name = "PurchaseOrder"


from .views import bp
from .models import PurchaseOrder, PurchaseOrderDetail
