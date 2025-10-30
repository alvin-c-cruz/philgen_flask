app_name = "plastic_label_adjustment"
app_label = "Plastic Label Adjustment"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticLabelAdjustment, PlasticLabelAdjustmentDetail
