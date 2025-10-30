app_name = "issuance"
app_label = "Issuance"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import Issuance, IssuanceDetail
