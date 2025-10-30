from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import RawMaterial as Obj
from .models import UserRawMaterial as Preparer
from .models import AdminRawMaterial as Approver


@dataclass
class RawMaterialForm:
    id: int = None
    raw_material_name: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.raw_material_name = object.raw_material_name
        self.user_prepare = object.user_prepare

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                raw_material_name=self.raw_material_name
                )
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                raw_material_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(raw_material_id=self.id).first()

            if record:
                record.raw_material_name = self.raw_material_name
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('raw_material_id')
        self.raw_material_name = request_form.get('raw_material_name')

    def validate_on_submit(self):
        self.errors = {}

        if not self.raw_material_name:
            self.errors["raw_material_name"] = "Please type raw material name."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.raw_material_name) == func.lower(self.raw_material_name), Obj.id != self.id).first()
            if existing_:
                self.errors["raw_material_name"] = "Raw material name already exists."

        if not self.errors:
            return True
        else:
            return False    
 