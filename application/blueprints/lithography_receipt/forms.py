from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import LithographyReceipt, UserLithographyReceipt as Preparer
from datetime import datetime


@dataclass
class Form:
    id: int = None
    record_date: str = ""
    lithography_receipt_number: str = ""
    invoice_number: str = ""
    lithography_id: int = 0
    sheet_received: int = 0
    outs: int = 0
    net_amount: float = 0.0
    additional_charge: float = 0.0
    notes: str = ""
    submitted: str = ""
    cancelled: str = ""
    locked: bool = False

    user_prepare_id: int = None

    errors = {}

    def save(self):
        if self.id is None:
            # Add a new record
            new_record = LithographyReceipt(
                record_date=self.record_date,
                lithography_receipt_number=self.lithography_receipt_number,
                invoice_number=self.invoice_number,
                lithography_id=self.lithography_id,
                sheet_received=self.sheet_received,
                outs=self.outs,
                net_amount=self.net_amount,
                additional_charge=self.additional_charge,
                notes=self.notes
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id
            
            preparer = Preparer(
                lithography_receipt_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = LithographyReceipt.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(lithography_receipt_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.lithography_receipt_number = self.lithography_receipt_number
                record.invoice_number = self.invoice_number
                record.lithography_id = self.lithography_id
                record.sheet_received = self.sheet_received
                record.outs = self.outs
                record.net_amount = self.net_amount
                record.additional_charge = self.additional_charge
                record.notes = self.notes
                record.submitted = self.submitted
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.lithography_receipt_number = obj.lithography_receipt_number
        self.invoice_number = obj.invoice_number
        self.lithography_id = obj.lithography_id
        self.sheet_received = obj.sheet_received
        self.outs = obj.outs
        self.net_amount = obj.net_amount
        self.additional_charge = obj.additional_charge
        self.notes = obj.notes
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled

    def post(self, request_form):
        self.id = request_form.get('lithography_receipt_id')
        self.record_date = request_form.get('record_date')
        self.lithography_receipt_number = request_form.get('lithography_receipt_number')
        self.invoice_number = request_form.get('invoice_number')
        self.lithography_id = int(request_form.get('lithography_id'))
        self.sheet_received = int(request_form.get('sheet_received'))
        self.outs = int(request_form.get('outs'))
        self.net_amount = float(request_form.get('net_amount'))
        self.additional_charge = float(request_form.get('additional_charge'))
        self.notes = request_form.get('notes')


    def validate_on_submit(self):
        self.errors = {}

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.lithography_receipt_number:
            self.errors["lithography_receipt_number"] = "Please type receipt number."
        else:
            duplicate = LithographyReceipt.query.filter(func.lower(LithographyReceipt.lithography_receipt_number) == func.lower(self.lithography_receipt_number), LithographyReceipt.id != self.id).first()
            if duplicate:
                self.errors["lithography_receipt_number"] = "Receiving report number is already used, please verify."        

        if not self.lithography_id:
            self.errors["lithography_id"] = "Please select description."

        if not self.errors:
            return True        
    
    def submit(self):
        self.submitted = str(datetime.today())[:10]

    @property
    def locked_(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
    