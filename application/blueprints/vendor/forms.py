from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Vendor as Obj
from .models import UserVendor as Preparer
from .models import AdminVendor as Approver


@dataclass
class Form:
    id: int = None
    vendor_name: str = ""
    registered_name: str = ""
    tin: str = ""
    business_style: str = ""
    address: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.vendor_name = object.vendor_name
        self.registered_name = object.registered_name
        self.tin = object.tin
        self.business_style = object.business_style
        self.address = object.address
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                vendor_name=self.vendor_name,
                registered_name=self.registered_name,
                tin=self.tin,
                business_style=self.business_style,
                address=self.address
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                vendor_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(vendor_id=self.id).first()

            if record:
                record.vendor_name = self.vendor_name
                record.registered_name = self.registered_name
                record.tin = self.tin
                record.business_style = self.business_style
                record.address = self.address
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('vendor_id')
        self.vendor_name = request_form.get('vendor_name')
        self.registered_name = request_form.get('registered_name')
        self.tin = request_form.get('tin')
        self.business_style = request_form.get('business_style')
        self.address = request_form.get('address')

    def validate_on_submit(self):
        self.errors = {}

        if not self.vendor_name:
            self.errors["vendor_name"] = "Please type vendor alias."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.vendor_name) == func.lower(self.vendor_name), Obj.id != self.id).first()
            if existing_:
                self.errors["vendor_name"] = "Vendor alias already exists."

        if not self.registered_name:
            self.errors["registered_name"] = "Please type registered name."

        if self.tin:
            existing_ = Obj.query.filter(
                func.lower(Obj.tin) == func.lower(self.tin), 
                func.lower(Obj.vendor_name) != func.lower(self.vendor_name), 
                Obj.id != self.id).first()
            if existing_:
                self.errors["tin"] = "TIN already used."

        if not self.errors:
            return True
        else:
            return False    
