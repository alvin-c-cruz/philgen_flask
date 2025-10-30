app_name = "plastic_raw_material"
app_label = "Plastic Raw Material"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticRawMaterial
