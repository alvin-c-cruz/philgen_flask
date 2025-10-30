from application.extensions import db, short_date, long_date
import datetime
from collections import defaultdict


class PurchaseOrderExtra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    purchase_order_number = db.Column(db.String())

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = db.relationship('Vendor', backref='purchase_order_extras', lazy=True)

    discount_note = db.Column(db.String())
    discount = db.Column(db.Float())

    order_note = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    requested_by = db.Column(db.String())
    prepared_by = db.Column(db.String())
    checked_by = db.Column(db.String())
    approved_by = db.Column(db.String())
    
    currency = db.Column(db.String(), default="PHP")
    terms = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserPurchaseOrderExtra.query.filter(UserPurchaseOrderExtra.purchase_order_extra_id==self.id).first()
        return obj

    @property
    def formatted_voucher_date(self):
        return long_date(self.record_date) if self.record_date else None

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None

    @property
    def formatted_submitted(self):
        return short_date(self.submitted) if self.submitted else None

    @property
    def formatted_cancelled(self):
        return short_date(self.cancelled) if self.cancelled else None

    @property
    def details_grouped_by_side_note(self):
        """
        Returns:
            dict[str, list[PurchaseOrderDetail]]: 
            A dictionary grouping purchase order details by their side_note.
        """
        grouped = defaultdict(list)
        for detail in self.purchase_order_extra_details:
            key = detail.side_note or 'No Note'
            grouped[key].append(detail)
        return grouped
    
    @property
    def total_amount(self):
        total = 0
        for detail in self.purchase_order_extra_details:
            total += detail.amount
        return total

    @property
    def net_amount(self):
        return self.total_amount - self.discount
        
    @property
    def formatted_total_amount(self):
        return '{:,.2f}'.format(self.total_amount)
    
    @property
    def purchase_request_numbers(self):
        requests = []
        for detail in self.purchase_order_extra_details:
            requests.append(detail.purchase_request_number)
            
        return ', '.join(sorted(set(requests)))

    @property
    def formatted_discount(self):
        return '{:,.2f}'.format(self.discount)
    
    @property
    def formatted_net_amount(self):
        return '{:,.2f}'.format(self.net_amount)
        

class PurchaseOrderExtraDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    purchase_request_number = db.Column(db.String())

    purchase_order_extra_id = db.Column(db.Integer, db.ForeignKey('purchase_order_extra.id'), nullable=False)
    purchase_order_extra = db.relationship('PurchaseOrderExtra', backref='purchase_order_extra_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='purchase_order_extra_details', lazy=True)

    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    raw_material = db.relationship('RawMaterial', backref='purchase_order_extra_details', lazy=True)

    unit_price = db.Column(db.Float, default=0)

    side_note = db.Column(db.String())

    @property
    def formatted_quantity(self):
        # Convert to string with enough precision to catch all decimals
        qty_str = f'{self.quantity:.10f}'.rstrip('0').rstrip('.')  # remove trailing zeros and dot if needed
        
        if '.' in qty_str:
            decimals = len(qty_str.split('.')[1])
        else:
            decimals = 0
        
        # Cap decimals to a max (e.g., 4)
        max_decimals = 4
        decimals = min(decimals, max_decimals)

        fmt = f'{{:,.{decimals}f}}'
        return fmt.format(self.quantity)

    @property
    def amount(self):
        return self.quantity * self.unit_price


    @property
    def formatted_unit_price(self):
        if self.unit_price is None:
            return ''
        
        # Check if more than 2 decimal places are non-zero
        if round(self.unit_price, 4) != round(self.unit_price, 2):
            return '{:,.4f}'.format(self.unit_price)
        else:
            return '{:,.2f}'.format(self.unit_price)
    
    @property
    def formatted_amount(self):
        return '{:,.2f}'.format(self.quantity * self.unit_price)
    
    
class UserPurchaseOrderExtra(db.Model):
    purchase_order_extra_id = db.Column(db.Integer, db.ForeignKey('purchase_order_extra.id'), primary_key=True)
    purchase_order_extra = db.relationship('PurchaseOrderExtra', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='purchase_order_extra_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPurchaseOrderExtra(db.Model):
    purchase_order_extra_id = db.Column(db.Integer, db.ForeignKey('purchase_order_extra.id'), primary_key=True)
    purchase_order_extra = db.relationship('PurchaseOrderExtra', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='purchase_order_extra_approved', lazy=True)

