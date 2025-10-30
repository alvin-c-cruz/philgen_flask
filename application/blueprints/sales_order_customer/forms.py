from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import SalesOrderCustomer as Obj
from .models import UserSalesOrderCustomer as Preparer
from .models import AdminSalesOrderCustomer as Approver


@dataclass
class Form:
    id: int = None
    customer_name: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.customer_name = object.customer_name
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                customer_name=self.customer_name,
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                sales_order_customer_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(sales_order_customer_id=self.id).first()

            if record:
                record.customer_name = self.customer_name
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('record_id')
        self.customer_name = request_form.get('customer_name')

    def validate_on_submit(self):
        self.errors = {}

        if not self.customer_name:
            self.errors["customer_name"] = "Please type customer name."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.customer_name) == func.lower(self.customer_name), Obj.id != self.id).first()
            if existing_:
                self.errors["customer_name"] = "Customer name already exists."

        if not self.errors:
            return True
        else:
            return False    
