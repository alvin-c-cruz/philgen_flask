from flask import flash
from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import PurchaseOrder as Obj
from .models import PurchaseOrderDetail as ObjDetail
from .models import UserPurchaseOrder as Preparer
from datetime import datetime
from . import app_name


DETAIL_ROWS = 10
    

def get_attributes(object):
    attributes = [x for x in dir(object) if (not x.startswith("_"))]
    exceptions = (
        "user_prepare_id", 
        "user_prepare", 
        "errors", 
        "active", 
        "details", 
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
    purchase_order_id:int = 0
    purchase_request_number: str = ""
    grouping: str = ""
    quantity: float = 0
    measure_id: int = 0
    description: str = ""
    unit_price: float = 0
    side_note: str = ""
    delivery_date: str = ""

    errors = {}

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def _populate(self, row):
        for attribute in get_attributes(self):
            if attribute in ["errors", "amount"]:
                continue
            elif attribute in ["measure_id"]:
                setattr(self, attribute, int(getattr(row, attribute)))
            elif attribute in ["quantity", "unit_price"]:
                setattr(self, attribute, float(getattr(row, attribute)))
            else:
                setattr(self, attribute, getattr(row, attribute))

    def _validate(self):
        self.errors = {}

        if self._is_dirty():            
            if not self.purchase_request_number:
                self.errors["purchase_request_number"] = "Please type purchase request number."

            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_id:
                self.errors["measure_id"] = "Please select measure."

            if not self.description:
                self.errors["description"] = "Please type description."
                                
        if not self.errors:
            return True
        else:
            return False    

    def _is_dirty(self):
        return any([
            self.purchase_request_number, 
            self.grouping, 
            self.quantity, 
            self.measure_id, 
            self.description, 
            self.unit_price, 
            self.side_note,
            self.delivery_date])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    purchase_order_number: str = ""
    vendor_id: int = 0
    notes: str = ""
    submitted: str = ""
    cancelled: str = ""

    user_prepare_id: int = None

    details = []
    errors = {}

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def _save(self, submitted=None):
        if self.id is None:
            # Add a new record
            new_record = Obj(
                **get_attributes_as_dict(self)
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail._is_dirty():
                    _dict = get_attributes_as_dict(detail)
                    _dict.pop("id")
                    _dict.pop("amount")
                    _dict[f"{app_name}_id"] = new_record.id
                    new_detail = ObjDetail(**_dict)

                    db.session.add(new_detail)
                    db.session.commit()
                
            preparer = Preparer(**{f"{app_name}_id": new_record.id})
            preparer.user_id=self.user_prepare_id

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(**{f"{app_name}_id": self.id}).first()
                preparer.user_id = self.user_prepare_id

                for attribute in get_attributes(self):
                    if attribute == "id": continue
                    setattr(record, attribute, getattr(self, attribute))
                                    
                details = ObjDetail.query.filter(
                    getattr(ObjDetail, f"{app_name}_id")==self.id
                    )
                    
                for detail in details:
                    db.session.delete(detail)

                for i, detail in self.details:
                    if detail._is_dirty():
                        _dict = get_attributes_as_dict(detail)
                        _dict.pop("id")
                        _dict.pop("amount")
                        _dict[f"{app_name}_id"] = record.id
                        row_detail = ObjDetail(**_dict)
                        db.session.add(row_detail)
                    
        db.session.commit()

   
    def _populate(self, obj):
        for attribute in get_attributes(self):
            if attribute in ["vendor_id"]:
                setattr(self, attribute, int(getattr(obj, attribute)))
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
            elif attribute in ["vendor_id"]:
                setattr(self, attribute, int(getattr(request_form, "get")(attribute)))
            elif attribute in ("submitted", "cancelled"):
                continue
            else:
                setattr(self, attribute, getattr(request_form, "get")(attribute))

        for i in range(DETAIL_ROWS):
            for attribute in get_attributes(ObjDetail):
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
                elif attribute in ["unit_price"]:
                    setattr(self.details[i][1], attribute, float(request_form.get(f'{attribute}-{i}')))
                elif attribute in ["purchase_request_number", "grouping", "description", "side_note", "delivery_date"]:
                    setattr(self.details[i][1], attribute, request_form.get(f'{attribute}-{i}'))
                else:
                    continue
 

    def _validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.vendor_id:
            self.errors["vendor_id"] = "Please select vendor."

        if not self.purchase_order_number:
            self.errors["purchase_order_number"] = "Please type purchase order number."
        else:
            duplicate = Obj.query.filter(
                func.lower(
                    Obj.purchase_order_number
                    ) == func.lower(self.purchase_order_number), 
                    Obj.id != self.id
                    ).first()
            if duplicate:
                self.errors["purchase_order_number"] = "Purchase order number is already used, please verify."        

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
    def _locked(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
    