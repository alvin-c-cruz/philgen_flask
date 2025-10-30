from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Lithography as Obj
from .models import UserLithography as Preparer
from .models import AdminLithography as Approver


@dataclass
class Form:
    id: int = None
    lithography_name: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.lithography_name = object.lithography_name
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                lithography_name=self.lithography_name,
                active=True
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                lithography_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(lithography_id=self.id).first()

            if record:
                record.lithography_name = self.lithography_name
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('lithography_id')
        self.lithography_name = request_form.get('lithography_name')

    def validate_on_submit(self):
        self.errors = {}

        if not self.lithography_name:
            self.errors["lithography_name"] = "Please type description."

        else:
            existing_ = Obj.query.filter(
                func.lower(Obj.lithography_name) == func.lower(self.lithography_name), 
                Obj.id != self.id
                ).first()
            if existing_:
                self.errors["lithography_name"] = "Description already exists."

        if not self.errors:
            return True
        else:
            return False    
