app_name = "plastic_product_component_status"
app_label = "Plastic Component Status"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticProductComponentStatus
