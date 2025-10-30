app_name = "plastic_product_component_production"
app_label = "Plastic Component Production"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticProductComponentProduction, PlasticProductComponentProductionDetail
