app_name = "production_tincan"
app_label = "Production Tincan"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import ProductionTincan, ProductionTincanDetail
