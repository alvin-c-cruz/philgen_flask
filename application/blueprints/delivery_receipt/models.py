from application.extensions import db, short_date, long_date
import datetime


class DeliveryReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    delivery_receipt_number = db.Column(db.String())
    po_number = db.Column(db.String())

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref='delivery_receipts', lazy=True)

    salesman = db.Column(db.String())
    checked_by = db.Column(db.String())
    approved_by = db.Column(db.String())
    carrier = db.Column(db.String())

    notes = db.Column(db.String())

    stacking = db.Column(db.String())
    production_date = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserDeliveryReceipt.query.filter(UserDeliveryReceipt.delivery_receipt_id==self.id).first()
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


class DeliveryReceiptDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    job_order_number = db.Column(db.String())

    delivery_receipt_id = db.Column(db.Integer, db.ForeignKey('delivery_receipt.id'), nullable=False)
    delivery_receipt = db.relationship('DeliveryReceipt', backref='delivery_receipt_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='delivery_receipt_details', lazy=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='delivery_receipt_details', lazy=True)

    side_note = db.Column(db.String())

    @property
    def formatted_quantity(self):
        return '{:,.0f}'.format(self.quantity)
    
    def __str__(self):
        return f"DR detail no. {self.id}"


class UserDeliveryReceipt(db.Model):
    delivery_receipt_id = db.Column(db.Integer, db.ForeignKey('delivery_receipt.id'), primary_key=True)
    delivery_receipt = db.relationship('DeliveryReceipt', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='delivery_receipt_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminDeliveryReceipt(db.Model):
    delivery_receipt_id = db.Column(db.Integer, db.ForeignKey('delivery_receipt.id'), primary_key=True)
    delivery_receipt = db.relationship('DeliveryReceipt', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='delivery_receipt_approved', lazy=True)

