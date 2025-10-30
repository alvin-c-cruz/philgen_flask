from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Customer as Obj
from .models import UserCustomer as Preparer
from .models import AdminCustomer as Approver


@dataclass
class Form:
    id: int = None
    customer_name: str = ""
    registered_name: str = ""
    tin: str = ""
    business_style: str = ""
    address: str = ""
    delivery_address: str = ""
    customer_code: str = ""
    salesman: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.customer_name = object.customer_name
        self.registered_name = object.registered_name
        self.tin = object.tin
        self.business_style = object.business_style
        self.address = object.address
        self.delivery_address = object.delivery_address
        self.customer_code = object.customer_code
        self.salesman = object.salesman
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                customer_name=self.customer_name,
                registered_name=self.registered_name,
                tin=self.tin,
                business_style=self.business_style,
                address=self.address,
                delivery_address=self.delivery_address,
                customer_code=self.customer_code,
                salesman=self.salesman
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                customer_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(customer_id=self.id).first()

            if record:
                record.customer_name = self.customer_name
                record.registered_name = self.registered_name
                record.tin = self.tin
                record.business_style = self.business_style
                record.address = self.address
                record.delivery_address = self.delivery_address
                record.customer_code = self.customer_code
                record.salesman = self.salesman
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('customer_id')
        self.customer_name = request_form.get('customer_name')
        self.registered_name = request_form.get('registered_name')
        self.tin = request_form.get('tin')
        self.business_style = request_form.get('business_style')
        self.address = request_form.get('address')
        self.delivery_address = request_form.get('delivery_address')
        self.customer_code = request_form.get('customer_code')
        self.salesman = request_form.get('salesman')

    def validate_on_submit(self):
        self.errors = {}

        if not self.customer_name:
            self.errors["customer_name"] = "Please type customer alias."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.customer_name) == func.lower(self.customer_name), Obj.id != self.id).first()
            if existing_:
                self.errors["customer_name"] = "Customer alias already exists."

        if not self.registered_name:
            self.errors["registered_name"] = "Please type registered name."

        if self.tin:
            existing_ = Obj.query.filter(
                func.lower(Obj.tin) == func.lower(self.tin), 
                func.lower(Obj.customer_name) != func.lower(self.customer_name), 
                func.lower(Obj.registered_name) != func.lower(self.registered_name), 
                Obj.id != self.id).first()
            if existing_:
                self.errors["tin"] = "TIN already used."

        if not self.errors:
            return True
        else:
            return False    
