app_name = "plastic_label"
app_label = "Plastic Label"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticLabel
