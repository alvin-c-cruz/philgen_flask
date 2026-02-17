from application.extensions import db, short_date, long_date
from collections import defaultdict
from sqlalchemy import or_, and_


class JobOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    job_order_number = db.Column(db.String())

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref='job_orders', lazy=True)

    customer_reference_number = db.Column(db.String())
    order_note = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    prepared_by = db.Column(db.String())
    checked_by = db.Column(db.String())
    approved_by = db.Column(db.String())
    
    done = db.Column(db.Boolean())

    @property
    def preparer(self):
        obj = UserJobOrder.query.filter(UserJobOrder.job_order_id==self.id).first()
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
            dict[str, list[JobOrderDetail]]: 
            A dictionary grouping job order details by their side_note.
        """
        grouped = defaultdict(list)
        for detail in self.job_order_details:
            key = detail.side_note or 'No Note'
            grouped[key].append(detail)
        return grouped
    
    @property
    def total_amount(self):
        total = 0
        for detail in self.job_order_details:
            total += detail.amount
        return total
    
    @property
    def net_amount(self):
        return self.total_amount
    
    
    @property
    def formatted_total_amount(self):
        return '{:,.2f}'.format(self.total_amount)
    
    
    @property
    def formatted_net_amount(self):
        return '{:,.2f}'.format(self.net_amount)


class JobOrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    job_order_id = db.Column(db.Integer, db.ForeignKey('job_order.id'), nullable=False)
    job_order = db.relationship('JobOrder', backref='job_order_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='job_order_details', lazy=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='product_order_details', lazy=True)
    
    product_description = db.Column(db.String())

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
    
    def pending(self):
        from .. delivery_receipt import DeliveryReceipt, DeliveryReceiptDetail
        from .. delivery_receipt_extra import DeliveryReceiptExtra, DeliveryReceiptExtraDetail
        
        _pending = self.quantity
        
        dr_corp_details = DeliveryReceiptDetail.query.filter(
            DeliveryReceiptDetail.job_order_number == self.job_order.job_order_number,
            DeliveryReceiptDetail.measure == self.measure,
            DeliveryReceiptDetail.product == self.product,
            DeliveryReceiptDetail.delivery_receipt.has(
                and_(
                    # submitted MUST be truthy
                    DeliveryReceipt.submitted.isnot(None),
                    DeliveryReceipt.submitted != '',
                    DeliveryReceipt.submitted != False,

                    # cancelled MUST be falsy
                    or_(
                        DeliveryReceipt.cancelled.is_(None),
                        DeliveryReceipt.cancelled == '',
                        DeliveryReceipt.cancelled == False
                    )
                )
            )
        ).all()
        
        for dr_detail in dr_corp_details:
            _pending -= dr_detail.quantity
         
        dr_corp_details = DeliveryReceiptExtraDetail.query.filter(
            DeliveryReceiptExtraDetail.job_order_number == self.job_order.job_order_number,
            DeliveryReceiptExtraDetail.measure == self.measure,
            DeliveryReceiptExtraDetail.product == self.product,
            DeliveryReceiptExtraDetail.delivery_receipt_extra.has(
                and_(
                    # submitted MUST be truthy
                    DeliveryReceiptExtra.submitted.isnot(None),
                    DeliveryReceiptExtra.submitted != '',
                    DeliveryReceiptExtra.submitted != False,

                    # cancelled MUST be falsy
                    or_(
                        DeliveryReceiptExtra.cancelled.is_(None),
                        DeliveryReceiptExtra.cancelled == '',
                        DeliveryReceiptExtra.cancelled == False
                    )
                )
            )
        ).all()
        
        for dr_detail in dr_corp_details:
            _pending -= dr_detail.quantity

        return _pending

    @property
    def formatted_pending(self):
        # Convert to string with enough precision to catch all decimals
        qty_str = f'{self.pending():.10f}'.rstrip('0').rstrip('.')  # remove trailing zeros and dot if needed
        
        if '.' in qty_str:
            decimals = len(qty_str.split('.')[1])
        else:
            decimals = 0
        
        # Cap decimals to a max (e.g., 4)
        max_decimals = 4
        decimals = min(decimals, max_decimals)

        fmt = f'{{:,.{decimals}f}}'
        return fmt.format(self.pending())    
    
    
class UserJobOrder(db.Model):
    job_order_id = db.Column(db.Integer, db.ForeignKey('job_order.id'), primary_key=True)
    job_order = db.relationship('JobOrder', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='job_order_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminJobOrder(db.Model):
    job_order_id = db.Column(db.Integer, db.ForeignKey('job_order.id'), primary_key=True)
    job_order = db.relationship('JobOrder', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='job_order_approved', lazy=True)

