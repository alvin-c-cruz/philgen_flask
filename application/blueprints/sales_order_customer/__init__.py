app_name = "sales_order_customer"
app_label = "Sales Order Customer"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import SalesOrderCustomer
