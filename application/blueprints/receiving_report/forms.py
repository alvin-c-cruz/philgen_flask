from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import ReceivingReport, ReceivingReportDetail, UserReceivingReport as Preparer
from datetime import datetime


from .. raw_material.models import RawMaterial

DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    purchase_order_number: str = ""
    receiving_report_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    raw_material_id: int = 0
    notes: str = ""
    
    raw_material_name: str = ""

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.purchase_order_number = row.purchase_order_number
        self.receiving_report_id = row.receiving_report_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.raw_material_id = row.raw_material_id
        self.raw_material_name = row.raw_material.raw_material_name
        self.notes = row.notes

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

        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([
            self.purchase_order_number, 
            self.quantity, 
            self.measure_id, 
            self.raw_material_id, 
            self.raw_material_name,
            self.notes
            ])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    receiving_report_number: str = ""
    vendor_id: int = 0
    supporting_documents: str = ""
    submitted: str = ""
    cancelled: str = ""
    received_by: str = ""
    prepared_by: str = ""
    checked_by: str = ""
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
            new_record = ReceivingReport(
                record_date=self.record_date,
                receiving_report_number=self.receiving_report_number,
                vendor_id=self.vendor_id,
                supporting_documents=self.supporting_documents,
                submitted=self.submitted,
                received_by=self.received_by,
                prepared_by=self.prepared_by,
                checked_by=self.checked_by
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = ReceivingReportDetail(
                        receiving_report_id=new_record.id,
                        purchase_order_number=detail.purchase_order_number,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        raw_material_id=detail.raw_material_id,
                        notes=detail.notes                    
                    )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                receiving_report_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = ReceivingReport.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(receiving_report_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.receiving_report_number = self.receiving_report_number
                record.vendor_id = self.vendor_id
                record.supporting_documents = self.supporting_documents
                record.submitted = self.submitted
                record.received_by = self.received_by
                record.prepared_by = self.prepared_by
                record.checked_by = self.checked_by
                
                details = ReceivingReportDetail.query.filter(ReceivingReportDetail.receiving_report_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = ReceivingReportDetail(
                            receiving_report_id=record.id,
                            purchase_order_number=detail.purchase_order_number,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            raw_material_id=detail.raw_material_id,
                            notes=detail.notes
                            )
                        db.session.add(row_detail)               
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.receiving_report_number = obj.receiving_report_number
        self.vendor_id = obj.vendor_id
        self.supporting_documents = obj.supporting_documents
        self.received_by = obj.received_by
        self.prepared_by = obj.prepared_by
        self.checked_by = obj.checked_by
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled

        for i, row in enumerate(obj.receiving_report_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, order_form):
        self.id = order_form.get('record_id')
        self.record_date = order_form.get('record_date')
        self.receiving_report_number = order_form.get('receiving_report_number')
        self.vendor_id = int(order_form.get('vendor_id'))
        self.supporting_documents = order_form.get('supporting_documents')
        self.prepared_by = order_form.get('prepared_by')
        self.received_by = order_form.get('received_by')
        self.checked_by = order_form.get('checked_by')

        for i in range(DETAIL_ROWS):
            self.details[i][1].purchase_order_number = order_form.get(f'purchase_order_number-{i}')

            if type(order_form.get(f'quantity-{i}')) == str:
                quantity_value = order_form.get(f'quantity-{i}')
                if quantity_value.isnumeric() or (quantity_value.replace('.', '', 1).isdigit() and quantity_value.count('.') <= 1):
                    self.details[i][1].quantity = float(quantity_value)
                else:
                    self.details[i][1].quantity = 0
            else: 
                self.details[i][1].quantity = order_form.get(f'quantity-{i}')

            self.details[i][1].measure_id = int(order_form.get(f'measure_id-{i}'))

            raw_material_name = order_form.get(f'raw_material_name-{i}')
            self.details[i][1].raw_material_name = raw_material_name
            
            raw_material = RawMaterial.query.filter_by(raw_material_name=raw_material_name).first()
            if raw_material:
                self.details[i][1].raw_material_id = raw_material.id
            
            notes = order_form.get(f'notes-{i}')
            self.details[i][1].notes = notes

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.receiving_report_number:
            self.errors["receiving_report_number"] = "Please type reference number."
        else:
            duplicate = ReceivingReport.query.filter(func.lower(ReceivingReport.receiving_report_number) == func.lower(self.receiving_report_number), ReceivingReport.id != self.id).first()
            if duplicate:
                self.errors["receiving_report_number"] = "Reference is already used, please verify."        

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
        