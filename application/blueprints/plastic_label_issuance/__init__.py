app_name = "plastic_label_issuance"
app_label = "Plastic Label Issuance"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticLabelIssuance, PlasticLabelIssuanceDetail
