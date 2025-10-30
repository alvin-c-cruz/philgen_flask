app_name = "raw_material"
app_label = "Raw Material"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import RawMaterial
