app_name = "plastic_raw_material_return"
app_label = "Plastic Raw Material Return"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticRawMaterialReturn, PlasticRawMaterialReturnDetail
