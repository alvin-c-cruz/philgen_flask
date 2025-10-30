from application.extensions import db, short_date
import datetime


class ProductionTincan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    production_number = db.Column(db.String())

    notes = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    prepared_by = db.Column(db.String())
    approved_by = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserProductionTincan.query.filter(UserProductionTincan.production_tincan_id==self.id).first()
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


class ProductionTincanDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    production_tincan_id = db.Column(db.Integer, db.ForeignKey('production_tincan.id'), nullable=False)
    production_tincan = db.relationship('ProductionTincan', backref='production_tincan_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='production_tincan_details', lazy=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='production_tincan_details', lazy=True)

    side_note = db.Column(db.String())

    @property
    def formatted_quantity(self):
        return '{:,.2f}'.format(self.quantity)
    
    
class UserProductionTincan(db.Model):
    production_tincan_id = db.Column(db.Integer, db.ForeignKey('production_tincan.id'), primary_key=True)
    production_tincan = db.relationship('ProductionTincan', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='production_tincan_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminProductionTincan(db.Model):
    production_tincan_id = db.Column(db.Integer, db.ForeignKey('production_tincan.id'), primary_key=True)
    production_tincan = db.relationship('ProductionTincan', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='production_tincan_approved', lazy=True)

