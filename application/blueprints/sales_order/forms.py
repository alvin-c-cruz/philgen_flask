from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import SalesOrder, SalesOrderDetail, UserSalesOrder as Preparer
from datetime import datetime


DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    sales_order_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    product_id: int = 0
    customer_po_number: str = ""
    delivery_date: str = ""
    customer_id: int = 0

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.sales_order_id = row.sales_order_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.product_id = row.product_id
        self.customer_po_number = row.customer_po_number
        self.delivery_date = row.delivery_date
        self.customer_id = row.customer_id 

    def validate(self):
        self.errors = {}

        if self.is_dirty():
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_id:
                self.errors["measure_id"] = "Please select measure."

            if not self.product_id:
                self.errors["product_id"] = "Please select product."

            if not self.delivery_date:
                self.errors["delivery_date"] = "Please type when the product is needed by customer."

            if not self.customer_id:
                self.errors["customer_id"] = "Please select customer."

        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([self.quantity, self.measure_id, self.product_id, self.customer_po_number, self.delivery_date, self.customer_id])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    sales_order_number: str = ""
    sales_order_customer_id: int = 0
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
            new_record = SalesOrder(
                record_date=self.record_date,
                sales_order_number=self.sales_order_number,
                sales_order_customer_id=self.sales_order_customer_id,
                notes=self.notes
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = SalesOrderDetail(
                        sales_order_id=new_record.id,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        product_id=detail.product_id,
                        customer_po_number=detail.customer_po_number,
                        delivery_date=detail.delivery_date,
                        customer_id=detail.customer_id                    
                        )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                sales_order_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = SalesOrder.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(sales_order_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.sales_order_number = self.sales_order_number
                record.sales_order_customer_id = self.sales_order_customer_id
                record.notes = self.notes
                record.submitted = self.submitted
                
                details = SalesOrderDetail.query.filter(SalesOrderDetail.sales_order_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = SalesOrderDetail(
                            sales_order_id=record.id,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            product_id=detail.product_id,
                            customer_po_number=detail.customer_po_number,
                            delivery_date=detail.delivery_date,
                            customer_id=detail.customer_id
                            )
                        db.session.add(row_detail)
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.sales_order_number = obj.sales_order_number
        self.sales_order_customer_id = obj.sales_order_customer_id
        self.notes = obj.notes
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled

        for i, row in enumerate(obj.sales_order_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, request_form):
        self.id = request_form.get('sales_order_id')
        self.record_date = request_form.get('record_date')
        self.sales_order_number = request_form.get('sales_order_number')
        self.sales_order_customer_id = int(request_form.get('sales_order_customer_id'))
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

            self.details[i][1].product_id = int(request_form.get(f'product_id-{i}'))
            self.details[i][1].customer_po_number = request_form.get(f'customer_po_number-{i}')
            self.details[i][1].delivery_date = request_form.get(f'delivery_date-{i}')
            self.details[i][1].customer_id = int(request_form.get(f'customer_id-{i}'))

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.sales_order_number:
            self.errors["sales_order_number"] = "Please type reference number."
        else:
            duplicate = SalesOrder.query.filter(func.lower(SalesOrder.sales_order_number) == func.lower(self.sales_order_number), SalesOrder.id != self.id).first()
            if duplicate:
                self.errors["sales_order_number"] = "Reference is already used, please verify."        

        if not self.sales_order_customer_id:
            self.errors["sales_order_customer_id"] = "Please select customer."


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
    