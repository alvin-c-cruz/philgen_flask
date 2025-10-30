app_name = "purchase_order_extra"
app_label = "Purchase Order Extra"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PurchaseOrderExtra, PurchaseOrderExtraDetail
