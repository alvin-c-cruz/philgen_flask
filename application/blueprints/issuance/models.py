from application.extensions import db, short_date
import datetime
from sqlalchemy.orm import joinedload


class Issuance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    issuance_number = db.Column(db.String())

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='issuances', lazy=True)

    notes = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    requested_by = db.Column(db.String())
    prepared_by = db.Column(db.String())
    checked_by = db.Column(db.String())
    approved_by = db.Column(db.String())
    
    done = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserIssuance.query.filter(UserIssuance.issuance_id==self.id).first()
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
    

class IssuanceDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    issuance_id = db.Column(db.Integer, db.ForeignKey('issuance.id'), nullable=False)
    issuance = db.relationship('Issuance', backref='issuance_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='issuance_details', lazy=True)

    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    raw_material = db.relationship('RawMaterial', backref='issuance_details', lazy=True)

    side_note = db.Column(db.String())

    @property
    def formatted_quantity(self):
        return '{:,.2f}'.format(self.quantity)
    
    
class UserIssuance(db.Model):
    issuance_id = db.Column(db.Integer, db.ForeignKey('issuance.id'), primary_key=True)
    issuance = db.relationship('Issuance', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='issuance_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminIssuance(db.Model):
    issuance_id = db.Column(db.Integer, db.ForeignKey('issuance.id'), primary_key=True)
    issuance = db.relationship('Issuance', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='issuance_approved', lazy=True)

