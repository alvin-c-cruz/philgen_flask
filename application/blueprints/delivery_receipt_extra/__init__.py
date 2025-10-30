app_name = "delivery_receipt_extra"
app_label = "Delivery Receipt Extra"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import DeliveryReceiptExtra, DeliveryReceiptExtraDetail
