from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Operator as Obj
from .models import UserOperator as Preparer
from .models import AdminOperator as Approver


@dataclass
class Form:
    id: int = None
    last_name: str = ""
    first_name: str = ""
    middle_name: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.last_name = object.last_name
        self.first_name = object.first_name
        self.middle_name = object.middle_name

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                last_name=self.last_name,
                first_name=self.first_name,
                middle_name=self.middle_name,
                )
    
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                operator_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(operator_id=self.id).first()

            if record:
                record.last_name = self.last_name
                record.first_name = self.first_name
                record.middle_name = self.middle_name

                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('record_id')
        self.last_name = request_form.get('last_name')
        self.first_name = request_form.get('first_name')
        self.middle_name = request_form.get('middle_name')

    def validate_on_submit(self):
        self.errors = {}

        if not self.last_name:
            self.errors["last_name"] = "Please type last name."
            
        if not self.first_name:
            self.errors["first_name"] = "Please type first name."
            
            
        if self.last_name and self.first_name:
            existing_ = Obj.query.filter(
                func.lower(Obj.last_name) == func.lower(self.last_name),
                func.lower(Obj.middle_name) == func.lower(self.middle_name),
                func.lower(Obj.first_name) == func.lower(self.first_name),
                Obj.id != self.id
                ).first()
            if existing_:
                self.errors["last_name"] = "Employee already exists."


        if not self.errors:
            return True
        else:
            return False    
