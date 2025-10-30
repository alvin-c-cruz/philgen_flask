app_name = "lithography_receipt"
app_label = "Lithography Receipt"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import LithographyReceipt
