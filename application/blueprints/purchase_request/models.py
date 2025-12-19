from application.extensions import db, short_date
import datetime
from sqlalchemy.orm import joinedload
from .. purchase_order import PurchaseOrder, PurchaseOrderDetail


class PurchaseRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    purchase_request_number = db.Column(db.String())

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='purchase_requests', lazy=True)

    request_note = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    requested_by = db.Column(db.String())
    prepared_by = db.Column(db.String())
    checked_by = db.Column(db.String())
    approved_by = db.Column(db.String())
    
    done = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserPurchaseRequest.query.filter(UserPurchaseRequest.purchase_request_id==self.id).first()
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
    
    def balance(self):
        # Get a list of purchases order indicating the purchase order number
        purchase_orders = (
            db.session.query(PurchaseOrder)
            .join(PurchaseOrderDetail)
            .filter(PurchaseOrderDetail.purchase_request_number == self.purchase_request_number,
                    PurchaseOrder.cancelled.is_(None),
                    )
            .options(joinedload(PurchaseOrder.purchase_order_details))
            .all()
            )


        # Match Purchase Request versus Purchase Order
        purchase_requests = self.purchase_request_details.copy()
        
        for order in purchase_orders:
            for detail in order.purchase_order_details:
                for request in purchase_requests:
                    if request.raw_material == detail.raw_material:
                        request.quantity -= detail.quantity
                        
        with_balance = []
        
        for request in purchase_requests:
            if request.quantity != 0:
                with_balance.append(request)
        
        return with_balance


class PurchaseRequestDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_request.id'), nullable=False)
    purchase_request = db.relationship('PurchaseRequest', backref='purchase_request_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='purchase_request_details', lazy=True)

    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    raw_material = db.relationship('RawMaterial', backref='purchase_request_details', lazy=True)

    date_needed = db.Column(db.String())
    side_note = db.Column(db.String())

    @property
    def formatted_date_needed(self):
        return short_date(self.date_needed) if self.date_needed else None

    @property
    def formatted_quantity(self):
        return '{:,.2f}'.format(self.quantity)
    
    
class UserPurchaseRequest(db.Model):
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_request.id'), primary_key=True)
    purchase_request = db.relationship('PurchaseRequest', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='purchase_request_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPurchaseRequest(db.Model):
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_request.id'), primary_key=True)
    purchase_request = db.relationship('PurchaseRequest', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='purchase_request_approved', lazy=True)

