from application.extensions import db, short_date, long_date
import datetime


class DeliveryReceiptExtra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    delivery_receipt_extra_number = db.Column(db.String())
    po_number = db.Column(db.String())

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref='delivery_receipts_extra', lazy=True)

    salesman = db.Column(db.String())
    prepared_by = db.Column(db.String())
    checked_by = db.Column(db.String())
    approved_by = db.Column(db.String())

    terms = db.Column(db.String())

    notes = db.Column(db.String())
    truck_number = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserDeliveryReceiptExtra.query.filter(UserDeliveryReceiptExtra.delivery_receipt_extra_id==self.id).first()
        return obj

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None

    @property
    def formatted_record_date_dr(self):
        return long_date(self.record_date) if self.record_date else None

    @property
    def formatted_submitted(self):
        return short_date(self.submitted) if self.submitted else None

    @property
    def formatted_cancelled(self):
        return short_date(self.cancelled) if self.cancelled else None
    
    def is_submitted(self):
        return True if self.submitted else False


class DeliveryReceiptExtraDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    job_order_number = db.Column(db.String())

    delivery_receipt_extra_id = db.Column(db.Integer, db.ForeignKey('delivery_receipt_extra.id'), nullable=False)
    delivery_receipt_extra = db.relationship('DeliveryReceiptExtra', backref='delivery_receipt_extra_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='delivery_receipt_extra_details', lazy=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='delivery_receipt_extra_details', lazy=True)

    so_number = db.Column(db.String())
    side_note = db.Column(db.String())

    @property
    def formatted_quantity(self):
        return '{:,.0f}'.format(self.quantity)


class UserDeliveryReceiptExtra(db.Model):
    delivery_receipt_extra_id = db.Column(db.Integer, db.ForeignKey('delivery_receipt_extra.id'), primary_key=True)
    delivery_receipt_extra = db.relationship('DeliveryReceiptExtra', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='delivery_receipt_extra_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminDeliveryReceiptExtra(db.Model):
    delivery_receipt_extra_id = db.Column(db.Integer, db.ForeignKey('delivery_receipt_extra.id'), primary_key=True)
    delivery_receipt_extra = db.relationship('DeliveryReceiptExtra', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='delivery_receipt_extra_approved', lazy=True)
