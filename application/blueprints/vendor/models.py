from application.extensions import db
from . import app_name, model_name


class Vendor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    vendor_name = db.Column(db.String(255))
    registered_name = db.Column(db.String(255))
    tin = db.Column(db.String(255))
    business_style = db.Column(db.String(255))
    address = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return getattr(self, f"{app_name}_name")
    
    @property
    def preparer(self):
        user_prepare = UserMeasure.query.filter(getattr(UserMeasure, f"{app_name}_id")==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminMeasure.query.filter(getattr(AdminMeasure, f"{app_name}_id")==self.id).first()
        return admin_approve


class UserMeasure(db.Model):
    measure_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    measure = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminMeasure(db.Model):
    measure_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    measure = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)
