app_name = "plastic_raw_material_issuance"
app_label = "Plastic Raw Material Issuance"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticRawMaterialIssuance, PlasticRawMaterialIssuanceDetail
