from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Measure as Obj
from .models import UserMeasure as Preparer
from .models import AdminMeasure as Approver


@dataclass
class Form:
    id: int = None
    measure_name: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.measure_name = object.measure_name
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                measure_name=self.measure_name
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                measure_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(measure_id=self.id).first()

            if record:
                record.measure_name = self.measure_name
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('measure_id')
        self.measure_name = request_form.get('measure_name')

    def validate_on_submit(self):
        self.errors = {}

        if not self.measure_name:
            self.errors["measure_name"] = "Please type measure name."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.measure_name) == func.lower(self.measure_name), Obj.id != self.id).first()
            if existing_:
                self.errors["measure_name"] = "Measure name already exists."

        if not self.errors:
            return True
        else:
            return False    
