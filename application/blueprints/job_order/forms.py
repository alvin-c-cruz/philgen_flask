from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import JobOrder as Obj, JobOrderDetail as ObjDetail, UserJobOrder as Preparer
from datetime import datetime

from .. product import Product
from .. measure import Measure
from .. customer import Customer


DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    job_order_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    product_id: int = 0
    product_description: str = ""
    unit_price: float = 0
    side_note: str = ""
    
    product_name: str = ""
    measure_name: str = ""

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.job_order_id = row.job_order_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.measure_name = row.measure.measure_name
        self.product_id = row.product_id
        self.product_name = row.product.product_name
        self.product_description = row.product_description if row.product_description else ""
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

            if not self.product_name:
                self.errors["product_name"] = "Please type item."
            else:
                product = Product.query.filter(Product.product_name==self.product_name).first()
                if not product:
                    self.errors["product_name"] = f"{self.product_name} does not exists."

        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([
            self.quantity, 
            self.measure_id, 
            self.measure_name,
            self.product_id, 
            self.product_name,
            self.product_description,
            self.side_note
            ])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    job_order_number: str = ""
    customer_id: int = 0
    customer_reference_number: str = ""
    order_note: str = ""

    submitted: str = ""
    cancelled: str = ""
    prepared_by: str = ""
    checked_by: str = ""
    approved_by: str = ""

    locked: bool = False

    user_prepare_id: int = None

    customer_name: str = ""

    details = []
    errors = {}

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def save(self):
        if self.id is None:
            # Add a new record
            new_record = Obj(
                record_date=self.record_date,
                job_order_number=self.job_order_number,
                customer_id=self.customer_id,
                order_note=self.order_note,
                customer_reference_number=self.customer_reference_number,
                submitted=self.submitted,
                prepared_by=self.prepared_by,
                checked_by=self.checked_by,
                approved_by=self.approved_by,
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = ObjDetail(
                        job_order_id=new_record.id,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        product_id=detail.product_id,
                        product_description=detail.product_description,
                        side_note=detail.side_note                    
                    )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                job_order_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(job_order_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.job_order_number = self.job_order_number
                record.customer_id = self.customer_id
                record.order_note = self.order_note
                record.customer_reference_number = self.customer_reference_number
                record.submitted = self.submitted
                record.prepared_by = self.prepared_by
                record.checked_by = self.checked_by
                record.approved_by = self.approved_by
                
                details = ObjDetail.query.filter(ObjDetail.job_order_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = ObjDetail(
                            job_order_id=record.id,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            product_id=detail.product_id,
                            product_description=detail.product_description,
                            side_note=detail.side_note
                            )
                        db.session.add(row_detail)          
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.job_order_number = obj.job_order_number
        self.customer_id = obj.customer_id
        self.customer_name = obj.customer.customer_name
        self.order_note = obj.order_note
        self.customer_reference_number = obj.customer_reference_number
        self.prepared_by = obj.prepared_by
        self.checked_by = obj.checked_by
        self.approved_by = obj.approved_by
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled

        for i, row in enumerate(obj.job_order_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, order_form):
        self.id = order_form.get('record_id')
        self.record_date = order_form.get('record_date')
        self.job_order_number = order_form.get('job_order_number')

        self.customer_name = order_form.get('customer_name')
        
        customer = Customer.query.filter(Customer.customer_name==self.customer_name).first()
        if customer:
            self.customer_id = customer.id
        else:
            self.customer_id = 0

        self.customer_reference_number = order_form.get('customer_reference_number')

        self.order_note = order_form.get('order_note')
        self.prepared_by = order_form.get('prepared_by')
        self.checked_by = order_form.get('checked_by')
        self.approved_by = order_form.get('approved_by')

        for i in range(DETAIL_ROWS):
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
            
            product_name = order_form.get(f'product_name-{i}')
            self.details[i][1].product_name = product_name
            
            product = Product.query.filter_by(product_name=product_name).first()
            if product:
                self.details[i][1].product_id = product.id
                
            self.details[i][1].product_description = order_form.get(f'product_description-{i}')

            self.details[i][1].side_note = order_form.get(f'side_note-{i}')

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.job_order_number:
            self.errors["job_order_number"] = "Please type reference number."
        else:
            duplicate = Obj.query.filter(func.lower(Obj.job_order_number) == func.lower(self.job_order_number), Obj.id != self.id).first()
            if duplicate:
                self.errors["job_order_number"] = "Reference is already used, please verify."        

        if not self.customer_name:
            self.errors["customer_name"] = "Please type customer."
        else:
            customer = Customer.query.filter(Customer.customer_name==self.customer_name).first()
            if not customer:
                self.errors["customer_name"] = "Customer name does not exists."

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
    
