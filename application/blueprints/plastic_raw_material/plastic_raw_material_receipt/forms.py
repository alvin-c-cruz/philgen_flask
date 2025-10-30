from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import PlasticRawMaterialReceipt, PlasticRawMaterialReceiptDetail, UserPlasticRawMaterialReceipt as Preparer
from datetime import datetime


DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    plastic_raw_material_receipt_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    plastic_raw_material_id: int = 0
    side_note: str = ""

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.plastic_raw_material_receipt_id = row.plastic_raw_material_receipt_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.plastic_raw_material_id = row.plastic_raw_material_id
        self.side_note = row.side_note 

    def validate(self):
        self.errors = {}

        if self.is_dirty():            
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_id:
                self.errors["measure_id"] = "Please select measure."

            if not self.plastic_raw_material_id:
                self.errors["plastic_raw_material_id"] = "Please select description."
                
        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([self.quantity, self.measure_id, self.plastic_raw_material_id, self.side_note])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    plastic_raw_material_receipt_number: str = ""
    vendor_id: int = 0
    packing_list: str = ""
    notes: str = ""
    submitted: str = ""
    cancelled: str = ""
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
            new_record = PlasticRawMaterialReceipt(
                record_date=self.record_date,
                plastic_raw_material_receipt_number=self.plastic_raw_material_receipt_number,
                vendor_id=self.vendor_id,
                packing_list=self.packing_list,
                notes=self.notes
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = PlasticRawMaterialReceiptDetail(
                        plastic_raw_material_receipt_id=new_record.id,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        plastic_raw_material_id=detail.plastic_raw_material_id,
                        side_note=detail.side_note                    
                        )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                plastic_raw_material_receipt_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = PlasticRawMaterialReceipt.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(plastic_raw_material_receipt_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.plastic_raw_material_receipt_number = self.plastic_raw_material_receipt_number
                record.vendor_id = self.vendor_id
                record.packing_list = self.packing_list
                record.notes = self.notes
                record.submitted = self.submitted
                
                details = PlasticRawMaterialReceiptDetail.query.filter(PlasticRawMaterialReceiptDetail.plastic_raw_material_receipt_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = PlasticRawMaterialReceiptDetail(
                            plastic_raw_material_receipt_id=record.id,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            plastic_raw_material_id=detail.plastic_raw_material_id,
                            side_note=detail.side_note
                            )
                        db.session.add(row_detail)
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.plastic_raw_material_receipt_number = obj.plastic_raw_material_receipt_number
        self.vendor_id = obj.vendor_id
        self.packing_list = obj.packing_list
        self.notes = obj.notes
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled

        for i, row in enumerate(obj.plastic_raw_material_receipt_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, request_form):
        self.id = request_form.get('plastic_raw_material_receipt_id')
        self.record_date = request_form.get('record_date')
        self.plastic_raw_material_receipt_number = request_form.get('plastic_raw_material_receipt_number')
        self.vendor_id = int(request_form.get('vendor_id'))
        self.packing_list = request_form.get('packing_list')
        self.notes = request_form.get('notes')

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

            self.details[i][1].plastic_raw_material_id = int(request_form.get(f'plastic_raw_material_id-{i}'))
            self.details[i][1].side_note = request_form.get(f'side_note-{i}')

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.plastic_raw_material_receipt_number:
            self.errors["plastic_raw_material_receipt_number"] = "Please type receiving report number."
        else:
            duplicate = PlasticRawMaterialReceipt.query.filter(func.lower(PlasticRawMaterialReceipt.plastic_raw_material_receipt_number) == func.lower(self.plastic_raw_material_receipt_number), PlasticRawMaterialReceipt.id != self.id).first()
            if duplicate:
                self.errors["plastic_raw_material_receipt_number"] = "Receiving report number is already used, please verify."        

        if not self.vendor_id:
            self.errors["vendor_id"] = "Please select vendor."


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

    @property
    def locked_(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
    