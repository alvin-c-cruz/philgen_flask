from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import PurchaseRequest, PurchaseRequestDetail, UserPurchaseRequest as Preparer
from datetime import datetime


from .. raw_material.models import RawMaterial

DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    purchase_request_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    raw_material_id: int = 0
    date_needed: str = ""
    side_note: str = ""
    
    raw_material_name: str = ""

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.purchase_request_id = row.purchase_request_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.raw_material_id = row.raw_material_id
        self.raw_material_name = row.raw_material.raw_material_name
        self.date_needed = row.date_needed
        self.side_note = row.side_note 

    def validate(self):
        self.errors = {}

        if self.is_dirty():
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_id:
                self.errors["measure_id"] = "Please select measure."

            if not self.raw_material_name:
                self.errors["raw_material_name"] = "Please type item."
            else:
                raw_material = RawMaterial.query.filter(RawMaterial.raw_material_name==self.raw_material_name).first()
                if not raw_material:
                    self.errors["raw_material_name"] = f"{self.raw_material_name} does not exists."

            # if not self.date_needed:
            #     self.errors["date_needed"] = "Please type when the item is needed."


        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([
            self.quantity, 
            self.measure_id, 
            self.raw_material_id, 
            self.raw_material_name,
            self.date_needed, 
            self.side_note
            ])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    purchase_request_number: str = ""
    department_id: int = 0
    request_note: str = ""
    submitted: str = ""
    cancelled: str = ""
    requested_by: str = ""
    prepared_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    done: str = ""
    
    locked: bool = False

    user_prepare_id: int = None


    details = []
    errors = {}

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def save(self):
        if self.id is None:
            # Add a new record
            new_record = PurchaseRequest(
                record_date=self.record_date,
                purchase_request_number=self.purchase_request_number,
                department_id=self.department_id,
                request_note=self.request_note,
                submitted=self.submitted,
                requested_by=self.requested_by,
                prepared_by=self.prepared_by,
                checked_by=self.checked_by,
                approved_by=self.approved_by,
                done=self.done,
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = PurchaseRequestDetail(
                        purchase_request_id=new_record.id,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        raw_material_id=detail.raw_material_id,
                        date_needed=detail.date_needed,
                        side_note=detail.side_note                    
                    )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                purchase_request_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = PurchaseRequest.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(purchase_request_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.purchase_request_number = self.purchase_request_number
                record.department_id = self.department_id
                record.request_note = self.request_note
                record.submitted = self.submitted
                record.requested_by = self.requested_by
                record.prepared_by = self.prepared_by
                record.checked_by = self.checked_by
                record.approved_by = self.approved_by
                record.done = self.done
                
                details = PurchaseRequestDetail.query.filter(PurchaseRequestDetail.purchase_request_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = PurchaseRequestDetail(
                            purchase_request_id=record.id,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            raw_material_id=detail.raw_material_id,
                            date_needed=detail.date_needed,
                            side_note=detail.side_note
                            )
                        db.session.add(row_detail)
            
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.purchase_request_number = obj.purchase_request_number
        self.department_id = obj.department_id
        self.request_note = obj.request_note
        self.requested_by = obj.requested_by
        self.prepared_by = obj.prepared_by
        self.checked_by = obj.checked_by
        self.approved_by = obj.approved_by
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled
        self.done = obj.done

        for i, row in enumerate(obj.purchase_request_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, request_form):
        self.id = request_form.get('purchase_request_id')
        self.record_date = request_form.get('record_date')
        self.purchase_request_number = request_form.get('purchase_request_number')
        self.department_id = int(request_form.get('department_id'))
        self.request_note = request_form.get('request_note')
        self.prepared_by = request_form.get('prepared_by')
        self.requested_by = request_form.get('requested_by')
        self.checked_by = request_form.get('checked_by')
        self.approved_by = request_form.get('approved_by')

        for i in range(DETAIL_ROWS):
            if type(request_form.get(f'quantity-{i}')) == str:
                quantity_value = request_form.get(f'quantity-{i}')
                if quantity_value.isnumeric() or (quantity_value.replace('.', '', 1).isdigit() and quantity_value.count('.') <= 1):
                    self.details[i][1].quantity = float(quantity_value)
                else:
                    self.details[i][1].quantity = 0
            else: 
                self.details[i][1].quantity = request_form.get(f'quantity-{i}')

            self.details[i][1].measure_id = int(request_form.get(f'measure_id-{i}'))

            raw_material_name = request_form.get(f'raw_material_name-{i}')
            self.details[i][1].raw_material_name = raw_material_name
            
            raw_material = RawMaterial.query.filter_by(raw_material_name=raw_material_name).first()
            if raw_material:
                self.details[i][1].raw_material_id = raw_material.id
                
            self.details[i][1].date_needed = request_form.get(f'date_needed-{i}')
            self.details[i][1].side_note = request_form.get(f'side_note-{i}')

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.purchase_request_number:
            self.errors["purchase_request_number"] = "Please type reference number."
        else:
            duplicate = PurchaseRequest.query.filter(func.lower(PurchaseRequest.purchase_request_number) == func.lower(self.purchase_request_number), PurchaseRequest.id != self.id).first()
            if duplicate:
                self.errors["purchase_request_number"] = "Reference is already used, please verify."        

        if not self.department_id:
            self.errors["department_id"] = "Please select department."


        for i in range(DETAIL_ROWS):
            if not self.details[i][1].validate():
                detail_validation = False

        all_not_dirty = True
        for _, detail in self.details:
            if detail.is_dirty():
                all_not_dirty = False

        if all_not_dirty:
            self.errors["entry"] = "There should be at least one entry."       

        if not self.errors and detail_validation:
            return True        
    
    def submit(self):
        self.submitted = str(datetime.today())[:10]
        
    def set_done(self):
        self.done = str(datetime.today())[:10]
        

    @property
    def locked_(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
    
