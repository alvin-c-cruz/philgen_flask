from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import PlasticRawMaterial as Obj
from .models import UserPlasticRawMaterial as Preparer
from .models import AdminPlasticRawMaterial as Approver

from . import app_name


@dataclass
class Form:
    id: int = None
    plastic_raw_material_name: str = ""
    plastic_raw_material_code: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def _attributes(self):
        attributes = [x for x in dir(self) if (not x.startswith("_"))]
        for i in ("user_prepare_id", "user_prepare", "errors"):
            attributes.remove(i)
        return attributes

    def _populate(self, object):
        for i in self._attributes():
            setattr(self, i, getattr(object, i))

        self.user_prepare = object.user_prepare

    def _save(self):
        if self.id is None:
            # Add a new record

            _dict = {}
            for i in self._attributes(): _dict[i] = getattr(self, i)

            record = Obj(**_dict)
            record.active = True

            db.session.add(record)
            db.session.commit()

            _dict = {
                f"{app_name}_id": record.id
            }
            preparer = Preparer(**_dict)
            preparer.user_id = self.user_prepare_id

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(plastic_raw_material_id=self.id).first()

            if record:
                for i in self._attributes():
                    setattr(record, i, getattr(self, i))
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def _post(self, request_form):
        self.id = request_form.get(f'{app_name}_id')
        for i in self._attributes():
            if i != "id":
                setattr(self, i, request_form.get(i))

    def _validate_on_submit(self):
        self.errors = {}

        if not self.plastic_raw_material_name:
            self.errors["plastic_raw_material_name"] = "Please type plastic raw material description."

        if not self.plastic_raw_material_code:
            self.errors["plastic_raw_material_code"] = "Please type plastic raw material code."

        if self.plastic_raw_material_name and self.plastic_raw_material_code:
            existing_ = Obj.query.filter(
                func.lower(Obj.plastic_raw_material_name) == func.lower(self.plastic_raw_material_name), 
                func.lower(Obj.plastic_raw_material_code) == func.lower(self.plastic_raw_material_code), 
                Obj.id != self.id
                ).first()
            if existing_:
                self.errors["plastic_raw_material_code"] = "Plastic raw material description and code combination already exists."

        if not self.errors:
            return True
        else:
            return False    
