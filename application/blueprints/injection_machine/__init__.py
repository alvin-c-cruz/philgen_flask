app_name = "injection_machine"
app_label = "Injection Machine"
menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import InjectionMachine
