from application.extensions import db


class Vendor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    vendor_name = db.Column(db.String(255))
    registered_name = db.Column(db.String(255))
    tin = db.Column(db.String(255))
    business_style = db.Column(db.String(255))
    address = db.Column(db.String(255))

    def __str__(self):
        return self.vendor_name
    
    @property
    def preparer(self):
        user_prepare = UserVendor.query.filter(UserVendor.vendor_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminVendor.query.filter(AdminVendor.vendor_id==self.id).first()
        return admin_approve


class UserVendor(db.Model):
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), primary_key=True)
    vendor = db.relationship('Vendor', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='vendor_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminVendor(db.Model):
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), primary_key=True)
    vendor = db.relationship('Vendor', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='vendor_approved', lazy=True)
