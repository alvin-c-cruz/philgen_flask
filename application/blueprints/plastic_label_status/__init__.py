app_name = "plastic_label_status"
app_label = "Plastic Label Status"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticLabelStatus
