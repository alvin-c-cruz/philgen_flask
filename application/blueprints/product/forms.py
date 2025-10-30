from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Product as Obj
from .models import UserProduct as Preparer
from .models import AdminProduct as Approver


@dataclass
class Form:
    id: int = None
    inhouse_name: str = ""
    product_name: str = ""
    product_code: str = ""
    customer_code: str = ""
    default_price: float = 0.0
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.inhouse_name = object.inhouse_name
        self.product_name = object.product_name
        self.product_code = object.product_code
        self.customer_code = object.customer_code
        self.default_price = object.default_price
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                inhouse_name=self.inhouse_name,
                product_name=self.product_name,
                product_code=self.product_code,
                customer_code=self.customer_code,
                default_price=self.default_price,
                active=True
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                product_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(product_id=self.id).first()

            if record:
                record.inhouse_name = self.inhouse_name
                record.product_name = self.product_name
                record.product_code = self.product_code
                record.customer_code = self.customer_code
                record.default_price = self.default_price
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('product_id')
        self.inhouse_name = request_form.get('inhouse_name')
        self.product_name = request_form.get('product_name')
        self.product_code = request_form.get('product_code')
        self.customer_code = request_form.get('customer_code')
        self.default_price = request_form.get('default_price')

    def validate_on_submit(self):
        self.errors = {}

        if not self.inhouse_name:
            self.errors["inhouse_name"] = "Please type inhouse name."

        if not self.product_name:
            self.errors["product_name"] = "Please type product name."

        if self.inhouse_name and self.product_name:
            existing_ = Obj.query.filter(
                func.lower(Obj.inhouse_name) == func.lower(self.inhouse_name), 
                func.lower(Obj.product_name) == func.lower(self.product_name), 
                Obj.id != self.id
                ).first()
            if existing_:
                self.errors["inhouse_name"] = "Inhouse and product name combination already exists."

        if self.product_code:
            existing_ = Obj.query.filter(func.lower(Obj.product_code) == func.lower(self.product_code), Obj.id != self.id).first()
            if existing_:
                self.errors["product_code"] = "Product Code already used."

        if not self.errors:
            return True
        else:
            return False    
