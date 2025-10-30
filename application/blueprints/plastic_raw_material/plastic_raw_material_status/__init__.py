app_name = "plastic_raw_material_status"
app_label = "Plastic Raw Material Status"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticRawMaterialStatus
