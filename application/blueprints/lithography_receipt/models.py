from application.extensions import db, short_date
import datetime


class LithographyReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    lithography_receipt_number = db.Column(db.String())

    invoice_number = db.Column(db.String())

    lithography_id = db.Column(db.Integer, db.ForeignKey('lithography.id'), nullable=False)
    lithography = db.relationship('Lithography', backref='lithography', lazy=True)

    sheet_received = db.Column(db.Integer, default=0)
    outs = db.Column(db.Integer, default=0)
    net_amount = db.Column(db.Float, default=0)
    additional_charge = db.Column(db.Float, default=0)

    notes = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def __str__(self):
        return f"{self.lithography_receipt_number}"

    @property
    def preparer(self):
        obj = UserLithographyReceipt.query.filter(UserLithographyReceipt.lithography_receipt_id==self.id).first()
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


class UserLithographyReceipt(db.Model):
    lithography_receipt_id = db.Column(db.Integer, db.ForeignKey('lithography_receipt.id'), primary_key=True)
    lithography_receipt = db.relationship('LithographyReceipt', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='lithography_receipt_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminLithographyReceipt(db.Model):
    lithography_receipt_id = db.Column(db.Integer, db.ForeignKey('lithography_receipt.id'), primary_key=True)
    lithography_receipt = db.relationship('LithographyReceipt', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='lithography_receipt_approved', lazy=True)

