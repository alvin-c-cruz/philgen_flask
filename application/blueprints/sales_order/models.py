from application.extensions import db, short_date
from .. delivery_receipt import DeliveryReceiptDetail
from .. delivery_receipt_extra import DeliveryReceiptExtraDetail
import datetime


class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    sales_order_number = db.Column(db.String())

    sales_order_customer_id = db.Column(db.Integer, db.ForeignKey('sales_order_customer.id'), nullable=False)
    sales_order_customer = db.relationship('SalesOrderCustomer', backref='sales_orders', lazy=True)

    notes = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def is_submitted(self):
        return True if self.submitted else False

    @property
    def preparer(self):
        obj = UserSalesOrder.query.filter(UserSalesOrder.sales_order_id==self.id).first()
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
    
    @property
    def delivery_details(self):
        deliveries = DeliveryReceiptDetail.query.filter_by(so_number=self.sales_order_number).all()
        return deliveries

    @property
    def delivery_extra_details(self):
        deliveries = DeliveryReceiptExtraDetail.query.filter_by(so_number=self.sales_order_number).all()
        return deliveries

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None


    def for_delivery(self): 
        _dict = {}

        for order in self.sales_order_details:
            key = order.product.inhouse_name
            order_quantity = order.quantity
            if not key in _dict:
                _dict[key] = {
                    "order": order_quantity,
                    "delivered": 0,
                    "balance": order_quantity
                }
            else:
                _dict[key]["order"] += order_quantity
                _dict[key]["balance"] += order_quantity

        for delivery in self.delivery_details:
            if not delivery.delivery_receipt.submitted:
                continue
            
            if delivery.delivery_receipt.cancelled:
                continue
            
            key = delivery.product.inhouse_name
            delivered_quantity = delivery.quantity    
            if not key in _dict:
                _dict[key] =  {
                    "order": 0,
                    "delivered": delivered_quantity,
                    "balance": delivered_quantity * -1
                }
            else:
                _dict[key]["delivered"] += delivered_quantity
                _dict[key]["balance"] -= delivered_quantity

        for delivery in self.delivery_extra_details:
            if not delivery.delivery_receipt_extra.submitted:
                continue
            
            if delivery.delivery_receipt_extra.cancelled:
                continue
            
            key = delivery.product.inhouse_name 
            delivered_quantity = delivery.quantity    
            if not key in _dict:
                _dict[key] =  {
                    "order": 0,
                    "delivered": delivered_quantity,
                    "balance": delivered_quantity * -1
                }
            else:
                _dict[key]["delivered"] += delivered_quantity
                _dict[key]["balance"] -= delivered_quantity

        _list = []
        for key, value in _dict.items():
            if not value["balance"]:
                continue
            
            line = []
            line.append(key)
            line.append(value["order"])
            line.append(value["delivered"])
            line.append(value["balance"])
            line.append(key)
            
            _list.append(line)

        return _list


class SalesOrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), nullable=False)
    sales_order = db.relationship('SalesOrder', backref='sales_order_details', lazy=True)


    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='sales_order_details', lazy=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='sales_order_details', lazy=True)

    customer_po_number = db.Column(db.String())
    delivery_date = db.Column(db.String())

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer = db.relationship('Customer', backref='sales_order_details', lazy=True)

    @property
    def formatted_delivery_date(self):
        return short_date(self.delivery_date) if self.delivery_date else None

    @property
    def formatted_quantity(self):
        return "{:,.0f}".format(self.quantity) if self.quantity else ""
    
    def remaining_order(self):
        #  TODO: Needs to update formula 
        remaining = self.quantity
        return remaining
    
    def remaining_order_dict(self):
        return {
            "sales_order_detail_id": self.id,
            "customer_po_number": self.customer_po_number,
            "delivery_date": self.customer_po_number,
            "remaining_order": self.remaining_order()
        }


class UserSalesOrder(db.Model):
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), primary_key=True)
    sales_order = db.relationship('SalesOrder', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='sales_order_prepared', lazy=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def __repr__(self):
        return self.user.first_name + " " + self.user.last_name


class AdminSalesOrder(db.Model):
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), primary_key=True)
    sales_order = db.relationship('SalesOrder', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='sales_order_approved', lazy=True)

