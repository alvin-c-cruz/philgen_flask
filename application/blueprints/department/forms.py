from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Department as Obj
from .models import UserDepartment as Preparer
from .models import AdminDepartment as Approver


@dataclass
class Form:
    id: int = None
    department_name: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.department_name = object.department_name
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                department_name=self.department_name
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                department_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(department_id=self.id).first()

            if record:
                record.department_name = self.department_name
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('department_id')
        self.department_name = request_form.get('department_name')

    def validate_on_submit(self):
        self.errors = {}

        if not self.department_name:
            self.errors["department_name"] = "Please type department name."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.department_name) == func.lower(self.department_name), Obj.id != self.id).first()
            if existing_:
                self.errors["department_name"] = "Department name already exists."

        if not self.errors:
            return True
        else:
            return False    
