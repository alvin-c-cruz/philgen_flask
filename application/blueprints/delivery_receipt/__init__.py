app_name = "delivery_receipt"
app_label = "Delivery Receipt"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import DeliveryReceipt, DeliveryReceiptDetail
