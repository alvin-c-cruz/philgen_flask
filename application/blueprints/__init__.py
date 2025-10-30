from . import main
from . import user

from . import raw_material # Factory Supplies
from . import measure # For general use
from . import department # Company Sections
from . import purchase_request # For factory supplies

from . import purchase_order
from . import purchase_order_extra

from . import receiving_report
from . import issuance

from . import customer # Sales
from . import sales_order_customer #For Sales Orders only
from . import vendor
from . import shift
from . import injection_machine

from . import plastic_product_component
from . import plastic_product_component_status
from . import plastic_product_component_production

from . import product # As seen in DR and Invoice
from . import production_tincan

from . import sales_order # From customer Purchase Order
from . import delivery_receipt
from . import delivery_receipt_extra

# Plastic Label Inventory
from . import plastic_label
from . import plastic_label_status
from . import plastic_label_receipt
from . import plastic_label_issuance
from . import plastic_label_return
from . import plastic_label_adjustment

# Printed Sheet
from . import lithography
from . import lithography_receipt

from . plastic_raw_material import *

from . import employee
from . import operator
