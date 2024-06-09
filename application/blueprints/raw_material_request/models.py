from application.extensions import db, short_date
from . import app_name, model_name


class RawMaterialRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    raw_material_request_number = db.Column(db.String())

    notes = db.Column(db.String())

    active = db.Column(db.Boolean())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def __str__(self):
        return getattr(self, f"{app_name}_number")

    @property
    def preparer(self):
        obj = UserRawMaterialRequest.query.filter(getattr(UserRawMaterialRequest, f"{app_name}_id")==self.id).first()
        return obj

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None

    @property
    def formatted_submitted(self):
        return short_date(self.submitted) if self.submitted else None

    @property
    def formatted_cancelled(self):
        return short_date(self.cancelled) if self.cancelled else None
    
    def is_submitted(self):
        return True if self.submitted else False


class RawMaterialRequestDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    raw_material_request_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), nullable=False)
    raw_material_request = db.relationship(model_name, backref=f'{app_name}_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref=f'{app_name}_details', lazy=True)

    raw_material_id = db.Column(db.Integer, db.ForeignKey(f'raw_material.id'), nullable=False)
    raw_material = db.relationship('RawMaterial', backref=f'{app_name}_details', lazy=True)

    side_note = db.Column(db.String())


class UserRawMaterialRequest(db.Model):
    raw_material_request_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    raw_material_request = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminRawMaterialRequest(db.Model):
    raw_material_request_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    raw_material_request = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)
