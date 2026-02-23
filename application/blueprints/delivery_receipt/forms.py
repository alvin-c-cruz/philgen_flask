from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import DeliveryReceipt as Obj
from .models import DeliveryReceiptDetail as ObjDetail
from .models import UserDeliveryReceipt as Preparer
from datetime import datetime
from . import app_name

from .. customer.models import Customer
from .. product.models import Product
from .. measure.models import Measure


DETAIL_ROWS = 10


def get_attributes(object):
    attributes = [x for x in dir(object) if (not x.startswith("_"))]
    exceptions = (
        "user_prepare_id", 
        "user_prepare", 
        "errors", 
        "active", 
        "details",
        "locked", 
        app_name,
        )
    for i in exceptions:
        try:
            attributes.remove(i)
        except ValueError:
            pass
    return attributes


def get_attributes_as_dict(object):
    attributes = get_attributes(object)
    return {
        attribute: getattr(object, attribute)
        for attribute in attributes
    }


@dataclass
class SubForm:
    id: int = 0
    delivery_receipt_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    product_id: int = 0
    job_order_number: str = ""
    side_note: str = ""

    product_name: str = ""
    measure_name: str = ""

    errors = {}

    def _populate(self, row):
        for attribute in get_attributes(self):
            if attribute in ["errors", "amount", "product_name"]:
                continue
            elif attribute in ["product_id"]:
                product = Product.query.get(getattr(row, "product_id"))
                setattr(self, attribute, product.id)
                self.product_name = product.product_name
            elif attribute in ["measure_id"]:
                measure = Measure.query.get(getattr(row, "measure_id"))
                self.measure_name = measure.measure_name
            elif attribute in ["id"]:
                setattr(self, attribute, int(getattr(row, attribute)))
            elif attribute in ["quantity", "unit_price"]:
                setattr(self, attribute, float(getattr(row, attribute)))
            else:
                setattr(self, attribute, getattr(row, attribute))

    def _validate(self):
        self.errors = {}

        if self._is_dirty():            
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_name:
                self.errors["measure_name"] = "Please type measure name."
            else:
                measure = Measure.query.filter(Measure.measure_name==self.measure_name).first()
                if not measure:
                    self.errors["measure_name"] = f"{self.measure_name} does not exists."

            if not self.product_name:
                self.errors["product_name"] = "Please type product name."
            else:
                product = Product.query.filter(Product.product_name==self.product_name).first()
                if not product:
                    self.errors["product_name"] = f"{self.product_name} does not exists."

        if not self.errors:
            return True
        else:
            return False    

    def _is_dirty(self):
        return any([
            self.quantity, 
            self.measure_id, 
            self.measure_name, 
            self.product_id, 
            self.product_name,
            self.job_order_number, 
            self.side_note
            ])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    delivery_receipt_number: str = ""
    po_number: str = ""
    customer_id: int = 0
    salesman: str = ""
    checked_by: str = ""
    approved_by: str = ""
    carrier: str = ""
    notes: str = ""
    stacking: str = ""
    production_date: str = ""

    submitted: str = ""
    cancelled: str = ""
    locked: bool = False

    user_prepare_id: int = None
    
    customer_name: str = ""

    details = []
    errors = {}

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def _save(self):
        if self.id is None:
            # Add a new record
            _dict = get_attributes_as_dict(self)
            if "locked" in _dict: _dict.pop("locked")
            _dict.pop("customer_name")
            
            new_record = Obj(
                **_dict
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail._is_dirty():
                    _dict = get_attributes_as_dict(detail)
                    _dict.pop("id")
                    _dict.pop("product_name")
                    _dict[f"{app_name}_id"] = new_record.id
                    new_detail = ObjDetail(**_dict)
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                delivery_receipt_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(delivery_receipt_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                for attribute in get_attributes(self):
                    if attribute == "id": continue
                    setattr(record, attribute, getattr(self, attribute))
                                    
                details = ObjDetail.query.filter(
                    getattr(ObjDetail, f"{app_name}_id")==self.id
                    )
                
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail._is_dirty():
                        _dict = get_attributes_as_dict(detail)
                        _dict.pop("id")
                        _dict.pop("product_name")
                        _dict.pop("measure_name")
                        _dict[f"{app_name}_id"] = record.id
                        row_detail = ObjDetail(**_dict)
                        db.session.add(row_detail)
                
        db.session.commit()
   
    def _populate(self, obj):
        for attribute in get_attributes(self):
            if attribute in ["customer_id"]:
                setattr(self, attribute, int(getattr(obj, attribute)))
                customer = Customer.query.get(getattr(obj, attribute))
                self.customer_name = customer.customer_name
            elif attribute == "customer_name":
                pass
            else:
                setattr(self, attribute, getattr(obj, attribute))

        for i, row in enumerate(getattr(obj, f"{app_name}_details")):
            subform = SubForm()
            subform._populate(row)
            self.details[i] = (i, subform)

    def _post(self, request_form):
        for attribute in get_attributes(self):
            if attribute == "id":
                value = getattr(request_form, "get")("record_id")
                if value:
                    setattr(self, "id", int(value))
            elif attribute in ["customer_id"]:
                customer_name = request_form.get('customer_name')
                customer = Customer.query.filter_by(
                    customer_name=customer_name
                    ).first()
                if customer:
                    setattr(self, attribute, customer.id)
                self.customer_name = customer_name

            elif attribute in ("submitted", "cancelled"):
                continue
            else:
                setattr(self, attribute, getattr(request_form, "get")(attribute))

        for i in range(DETAIL_ROWS):
            for attribute in ["product_name"] + get_attributes(ObjDetail):
                if attribute == "quantity":
                    if type(request_form.get(f'quantity-{i}')) == str:
                        quantity_value = request_form.get(f'quantity-{i}')
                        if quantity_value.isnumeric() or (quantity_value.replace('.', '', 1).isdigit() and quantity_value.count('.') <= 1):
                            self.details[i][1].quantity = float(quantity_value)
                        else:
                            self.details[i][1].quantity = 0
                    else: 
                        self.details[i][1].quantity = float(request_form.get(f'quantity-{i}'))
                elif attribute in ["measure_id"]:
                    setattr(self.details[i][1], attribute, int(request_form.get(f'{attribute}-{i}')))
                elif attribute in ["product_name"]:
                    product_name = request_form.get(f'product_name-{i}')
                    setattr(self.details[i][1], attribute, product_name)
                    if product_name:
                        product = Product.query.filter_by(product_name=product_name).first()
                        setattr(self.details[i][1], "product_id", product.id)
                    
                elif attribute in ["so_number", "side_note"]:
                    setattr(self.details[i][1], attribute, request_form.get(f'{attribute}-{i}'))
                else:
                    continue
 

    def _validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.delivery_receipt_number:
            self.errors["delivery_receipt_number"] = "Please type delivery receipt number."
        else:
            duplicate = Obj.query.filter(
                func.lower(
                    Obj.delivery_receipt_number
                    ) == func.lower(self.delivery_receipt_number), 
                    Obj.id != self.id
                    ).first()
            if duplicate:
                self.errors["delivery_receipt_number"] = "Delivery receipt number is already used, please verify."        

        if not self.customer_name:
            self.errors["customer_name"] = "Please type customer."
        else:
            customer = Customer.query.filter(Customer.customer_name==self.customer_name).first()
            if not customer:
                self.errors["customer_name"] = f"{self.customer_name} does not exists."


        for i in range(DETAIL_ROWS):
            if not self.details[i][1]._validate():
                detail_validation = False

        all_not_dirty = True
        for _, detail in self.details:
            if detail._is_dirty():
                all_not_dirty = False

        if all_not_dirty:
            self.errors["entry"] = "There should be at least one entry."       

        if not self.errors and detail_validation:
            return True        
    
    def _submit(self):
        self.submitted = str(datetime.today())[:10]

    @property
    def _locked_(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
    