from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import RawMaterialRequest as Obj
from .models import RawMaterialRequestDetail as ObjDetail
from .models import UserRawMaterialRequest as Preparer
from datetime import datetime
from . import app_name, model_name


DETAIL_ROWS = 10
    

def get_attributes(object):
    attributes = [x for x in dir(object) if (not x.startswith("_"))]
    exceptions = (
        "user_prepare_id", 
        "user_prepare", 
        "errors", 
        "active", 
        "details", 
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
    raw_material_request_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    raw_material_id: int = 0
    side_note: str = ""

    errors = {}

    def _populate(self, row):
        for attribute in get_attributes(self):
            setattr(self, attribute, getattr(row, attribute))

    def _validate(self):
        self.errors = {}

        if self._is_dirty():            
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_id:
                self.errors["measure_id"] = "Please select measure."

            if not self.raw_material_id:
                self.errors["raw_material_id"] = "Please select description."
                                
        if not self.errors:
            return True
        else:
            return False    

    def _is_dirty(self):
        return any([self.quantity, self.measure_id, self.raw_material_id, self.side_note])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    raw_material_request_number: str = ""
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
                    new_detail = ObjDetail(**_dict)
                    setattr(new_detail, f"{app_name}_id", new_record.id)
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
                        _dict = {
                            f"{app_name}_id": record.id,
                            "quantity": detail.quantity,
                            "measure_id": detail.measure_id,
                            "raw_material_id": detail.raw_material_id,
                            "side_note": detail.side_note
                        }
                        row_detail = ObjDetail(**_dict)
                        db.session.add(row_detail)
                
        db.session.commit()
   
    def _populate(self, obj):
        for attribute in get_attributes(self):
            if attribute in []:
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
                value = getattr(request_form, "get")(f"{app_name}_id")
                if value:
                    setattr(self, "id", int(value))
            elif attribute in []:
                setattr(self, attribute, int(getattr(request_form, "get")(attribute)))
            elif attribute in ("submitted", "cancelled"):
                continue
            else:
                setattr(self, attribute, getattr(request_form, "get")(attribute))

        for i in range(DETAIL_ROWS):
            if type(request_form.get(f'quantity-{i}')) == str:
                quantity_value = request_form.get(f'quantity-{i}')
                if quantity_value.isnumeric() or (quantity_value.replace('.', '', 1).isdigit() and quantity_value.count('.') <= 1):
                    self.details[i][1].quantity = float(quantity_value)
                else:
                    self.details[i][1].quantity = 0
            else: 
                self.details[i][1].quantity = float(request_form.get(f'quantity-{i}'))

            self.details[i][1].measure_id = int(request_form.get(f'measure_id-{i}'))

            self.details[i][1].raw_material_id = int(request_form.get(f'raw_material_id-{i}'))
            self.details[i][1].side_note = request_form.get(f'side_note-{i}')

    def _validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.raw_material_request_number:
            self.errors["raw_material_request_number"] = "Please type request number."
        else:
            duplicate = Obj.query.filter(
                func.lower(
                    Obj.raw_material_request_number
                    ) == func.lower(self.raw_material_request_number), 
                    Obj.id != self.id
                    ).first()
            if duplicate:
                self.errors["raw_material_request_number"] = "Request number is already used, please verify."        

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
    