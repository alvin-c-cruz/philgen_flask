app_name = "plastic_label_return"
app_label = "Plastic Label Return"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import PlasticLabelReturn, PlasticLabelReturnDetail
