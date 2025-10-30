from application.extensions import db


class Customer(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    customer_name = db.Column(db.String(255))
    registered_name = db.Column(db.String(255))
    tin = db.Column(db.String(255))
    business_style = db.Column(db.String(255))
    address = db.Column(db.String(255))
    delivery_address = db.Column(db.String(255))
    customer_code = db.Column(db.String(255))
    salesman = db.Column(db.String(255))

    def __str__(self):
        return self.customer_name
    
    @property
    def preparer(self):
        user_customer = UserCustomer.query.filter(UserCustomer.customer_id==self.id).first()
        return user_customer
    
    @property
    def approved(self):
        admin_approve = AdminCustomer.query.filter(AdminCustomer.customer_id==self.id).first()
        return admin_approve


class UserCustomer(db.Model):
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    customer = db.relationship('Customer', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='customer_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminCustomer(db.Model):
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    customer = db.relationship('Customer', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='customer_approved', lazy=True)
