from application.extensions import db, short_date
import datetime


class PlasticLabelReturn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    plastic_label_return_number = db.Column(db.String())

    notes = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def __str__(self):
        return f"{self.plastic_label_return_number}"

    @property
    def preparer(self):
        obj = UserPlasticLabelReturn.query.filter(UserPlasticLabelReturn.plastic_label_return_id==self.id).first()
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


class PlasticLabelReturnDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    plastic_label_return_id = db.Column(db.Integer, db.ForeignKey('plastic_label_return.id'), nullable=False)
    plastic_label_return = db.relationship('PlasticLabelReturn', backref='plastic_label_return_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='plastic_label_return_details', lazy=True)

    plastic_label_id = db.Column(db.Integer, db.ForeignKey('plastic_label.id'), nullable=False)
    plastic_label = db.relationship('PlasticLabel', backref='plastic_label_return_details', lazy=True)

    plastic_label_status_id = db.Column(db.Integer, db.ForeignKey('plastic_label_status.id'), nullable=True)
    plastic_label_status = db.relationship('PlasticLabelStatus', backref='plastic_label_return_details', lazy=True)

    side_note = db.Column(db.String())


class UserPlasticLabelReturn(db.Model):
    plastic_label_return_id = db.Column(db.Integer, db.ForeignKey('plastic_label_return.id'), primary_key=True)
    plastic_label_return = db.relationship('PlasticLabelReturn', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_label_return_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticLabelReturn(db.Model):
    plastic_label_return_id = db.Column(db.Integer, db.ForeignKey('plastic_label_return.id'), primary_key=True)
    plastic_label_return = db.relationship('PlasticLabelReturn', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_label_return_approved', lazy=True)
