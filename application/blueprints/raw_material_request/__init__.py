app_name = "raw_material_request"
app_label = "Raw Material Request"
menu_label = (app_name, f"/{app_name}", app_label)
model_name = "RawMaterialRequest"


from .views import bp
from .models import RawMaterialRequest, RawMaterialRequestDetail
