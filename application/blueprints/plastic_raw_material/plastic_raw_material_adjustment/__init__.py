app_name = "plastic_raw_material_adjustment"
app_label = "Plastic Raw Material Adjustment"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticRawMaterialAdjustment, PlasticRawMaterialAdjustmentDetail
