app_name = "department"
app_label = "Department"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import Department
