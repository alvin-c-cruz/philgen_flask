app_name = "plastic_product_component"
app_label = "Plastic Product Component"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticProductComponent
