from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import PurchaseOrderExtra, PurchaseOrderExtraDetail, UserPurchaseOrderExtra as Preparer
from datetime import datetime


from .. raw_material.models import RawMaterial
from .. measure.models import Measure
from .. vendor.models import Vendor


DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    purchase_request_number: str = ""
    purchase_order_extra_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    raw_material_id: int = 0
    unit_price: float = 0
    side_note: str = ""
    
    raw_material_name: str = ""
    measure_name: str = ""

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.purchase_request_number = row.purchase_request_number
        self.purchase_order_extra_id = row.purchase_order_extra_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.measure_name = row.measure.measure_name
        self.raw_material_id = row.raw_material_id
        self.raw_material_name = row.raw_material.raw_material_name
        self.unit_price = row.unit_price
        self.side_note = row.side_note 

    def validate(self):
        self.errors = {}

        if self.is_dirty():
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_name:
                self.errors["measure_name"] = "Please type measure."
            else:
                measure = Measure.query.filter(Measure.measure_name==self.measure_name).first()
                if not measure:
                    self.error["measure_name"] = f"{self.measure_name} does not exists."

            if not self.raw_material_name:
                self.errors["raw_material_name"] = "Please type item."
            else:
                raw_material = RawMaterial.query.filter(RawMaterial.raw_material_name==self.raw_material_name).first()
                if not raw_material:
                    self.errors["raw_material_name"] = f"{self.raw_material_name} does not exists."

            if self.unit_price < 0:
                self.errors["unit_price"] = "Unit Price should be a positive number."

        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([
            self.purchase_request_number, 
            self.quantity, 
            self.measure_id, 
            self.measure_name,
            self.raw_material_id, 
            self.raw_material_name,
            self.unit_price, 
            self.side_note
            ])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    purchase_order_number: str = ""
    vendor_id: int = 0
    order_note: str = ""
    discount: float = 0.0
    discount_note: str = ""
    submitted: str = ""
    cancelled: str = ""
    requested_by: str = ""
    prepared_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    currency: str = ""
    terms: str = ""
    locked: bool = False

    user_prepare_id: int = None
    
    vendor_name: str = ""


    details = []
    errors = {}

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def save(self):
        if self.id is None:
            # Add a new record
            new_record = PurchaseOrderExtra(
                record_date=self.record_date,
                purchase_order_number=self.purchase_order_number,
                discount=self.discount,
                discount_note=self.discount_note,
                vendor_id=self.vendor_id,
                order_note=self.order_note,
                submitted=self.submitted,
                requested_by=self.requested_by,
                prepared_by=self.prepared_by,
                checked_by=self.checked_by,
                approved_by=self.approved_by,
                currency=self.currency,
                terms=self.terms
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = PurchaseOrderExtraDetail(
                        purchase_order_extra_id=new_record.id,
                        purchase_request_number=detail.purchase_request_number,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        raw_material_id=detail.raw_material_id,
                        unit_price=detail.unit_price,
                        side_note=detail.side_note                    
                    )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                purchase_order_extra_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = PurchaseOrderExtra.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(purchase_order_extra_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.purchase_order_number = self.purchase_order_number
                record.discount = self.discount
                record.discount_note = self.discount_note
                record.vendor_id = self.vendor_id
                record.order_note = self.order_note
                record.submitted = self.submitted
                record.requested_by = self.requested_by
                record.prepared_by = self.prepared_by
                record.checked_by = self.checked_by
                record.approved_by = self.approved_by
                record.currency = self.currency
                record.terms = self.terms
                
                details = PurchaseOrderExtraDetail.query.filter(PurchaseOrderExtraDetail.purchase_order_extra_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = PurchaseOrderExtraDetail(
                            purchase_order_extra_id=record.id,
                            purchase_request_number=detail.purchase_request_number,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            raw_material_id=detail.raw_material_id,
                            unit_price=detail.unit_price,
                            side_note=detail.side_note
                            )
                        db.session.add(row_detail)
            
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.purchase_order_number = obj.purchase_order_number
        self.vendor_id = obj.vendor_id
        self.vendor_name = obj.vendor.vendor_name
        self.order_note = obj.order_note
        self.discount = obj.discount
        self.discount_note = obj.discount_note
        self.requested_by = obj.requested_by
        self.prepared_by = obj.prepared_by
        self.checked_by = obj.checked_by
        self.approved_by = obj.approved_by
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled
        self.currency = obj.currency
        self.terms = obj.terms

        for i, row in enumerate(obj.purchase_order_extra_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, order_form):
        self.id = order_form.get('record_id')
        self.record_date = order_form.get('record_date')
        self.purchase_order_number = order_form.get('purchase_order_number')

        self.vendor_name = order_form.get('vendor_name')
        
        vendor = Vendor.query.filter(Vendor.vendor_name==self.vendor_name).first()
        if vendor:
            self.vendor_id = vendor.id
        else:
            self.vendor_id = 0

        self.order_note = order_form.get('order_note')

        _discount = order_form.get('discount')
        if not _discount.isnumeric():
            self.discount = 0
        else:
            self.discount = float(_discount)

        self.discount_note = order_form.get('discount_note')
        self.prepared_by = order_form.get('prepared_by')
        self.requested_by = order_form.get('requested_by')
        self.checked_by = order_form.get('checked_by')
        self.approved_by = order_form.get('approved_by')
        self.currency = order_form.get('currency')
        self.terms = order_form.get('terms')

        for i in range(DETAIL_ROWS):
            self.details[i][1].purchase_request_number = order_form.get(f'purchase_request_number-{i}')

            if type(order_form.get(f'quantity-{i}')) == str:
                quantity_value = order_form.get(f'quantity-{i}')
                if quantity_value.isnumeric() or (quantity_value.replace('.', '', 1).isdigit() and quantity_value.count('.') <= 1):
                    self.details[i][1].quantity = float(quantity_value)
                else:
                    self.details[i][1].quantity = 0
            else: 
                self.details[i][1].quantity = order_form.get(f'quantity-{i}')

            measure_name = order_form.get(f'measure_name-{i}')
            self.details[i][1].measure_name = measure_name

            measure = Measure.query.filter_by(measure_name=measure_name).first()
            if measure:
                self.details[i][1].measure_id = measure.id
            
            raw_material_name = order_form.get(f'raw_material_name-{i}')
            self.details[i][1].raw_material_name = raw_material_name
            
            raw_material = RawMaterial.query.filter_by(raw_material_name=raw_material_name).first()
            if raw_material:
                self.details[i][1].raw_material_id = raw_material.id
                
            self.details[i][1].unit_price = float(order_form.get(f'unit_price-{i}'))

            self.details[i][1].side_note = order_form.get(f'side_note-{i}')

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.purchase_order_number:
            self.errors["purchase_order_number"] = "Please type reference number."
        else:
            duplicate = PurchaseOrderExtra.query.filter(func.lower(PurchaseOrderExtra.purchase_order_number) == func.lower(self.purchase_order_number), PurchaseOrderExtra.id != self.id).first()
            if duplicate:
                self.errors["purchase_order_number"] = "Reference is already used, please verify."        

        if not self.vendor_name:
            self.errors["vendor_name"] = "Please type vendor."
        else:
            vendor = Vendor.query.filter(Vendor.vendor_name==self.vendor_name).first()
            if not vendor:
                self.errors["vendor_name"] = "Vendor name does not exists."

        if not str(self.discount).isnumeric():
            self.discount = 0

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
    