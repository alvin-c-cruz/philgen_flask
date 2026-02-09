from application.extensions import db


class Product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    product_name = db.Column(db.String(255))
    product_code = db.Column(db.String(255))
    customer_code = db.Column(db.String(255))
    default_price = db.Column(db.Float())
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.product_name
    
    @property
    def preparer(self):
        user_product = UserProduct.query.filter(UserProduct.product_id==self.id).first()
        return user_product
    
    @property
    def approved(self):
        admin_approve = AdminProduct.query.filter(AdminProduct.product_id==self.id).first()
        return admin_approve


class UserProduct(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    product = db.relationship('Product', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='product_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminProduct(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    product = db.relationship('Product', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='product_approved', lazy=True)
