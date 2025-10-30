app_name = "plastic_raw_material_receipt"
app_label = "Plastic Raw Material Receiving Report"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticRawMaterialReceipt, PlasticRawMaterialReceiptDetail
