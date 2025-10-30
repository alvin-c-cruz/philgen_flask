app_name = "sales_order"
app_label = "Sales Order"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import SalesOrder, SalesOrderDetail
