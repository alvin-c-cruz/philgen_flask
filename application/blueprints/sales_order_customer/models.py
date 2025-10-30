from application.extensions import db


class SalesOrderCustomer(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    customer_name = db.Column(db.String(255))

    def __str__(self):
        return self.customer_name
    
    @property
    def preparer(self):
        user_customer = UserSalesOrderCustomer.query.filter(UserSalesOrderCustomer.sales_order_customer_id==self.id).first()
        return user_customer
    
    @property
    def approved(self):
        admin_approve = AdminSalesOrderCustomer.query.filter(AdminSalesOrderCustomer.sales_order_customer_id==self.id).first()
        return admin_approve


class UserSalesOrderCustomer(db.Model):
    sales_order_customer_id = db.Column(db.Integer, db.ForeignKey('sales_order_customer.id'), primary_key=True)
    sales_order_customer = db.relationship('SalesOrderCustomer', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='sales_order_customer_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminSalesOrderCustomer(db.Model):
    sales_order_customer_id = db.Column(db.Integer, db.ForeignKey('sales_order_customer.id'), primary_key=True)
    sales_order_customer = db.relationship('SalesOrderCustomer', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='sales_order_customer_approved', lazy=True)
