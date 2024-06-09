from application.extensions import db
from . import app_name


class RawMaterial(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    raw_material_name = db.Column(db.String(255))
    raw_material_code = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return getattr(self, f"{app_name}_name")
    
    @property
    def preparer(self):
        user_prepare = UserRawMaterial.query.filter(getattr(UserRawMaterial, f"{app_name}_id")==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminRawMaterial.query.filter(getattr(AdminRawMaterial, f"{app_name}_id")==self.id).first()
        return admin_approve


class UserRawMaterial(db.Model):
    raw_material_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    raw_material = db.relationship('RawMaterial', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='raw_material_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminRawMaterial(db.Model):
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), primary_key=True)
    raw_material = db.relationship('RawMaterial', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='raw_material_approved', lazy=True)
