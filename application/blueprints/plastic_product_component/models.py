from application.extensions import db


class PlasticProductComponent(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    plastic_product_component_name = db.Column(db.String(255))
    plastic_product_component_code = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.plastic_product_component_name
    
    @property
    def preparer(self):
        user_prepare = UserPlasticProductComponent.query.filter(UserPlasticProductComponent.plastic_product_component_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminPlasticProductComponent.query.filter(AdminPlasticProductComponent.plastic_product_component_id==self.id).first()
        return admin_approve


class UserPlasticProductComponent(db.Model):
    plastic_product_component_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component.id'), primary_key=True)
    plastic_product_component = db.relationship('PlasticProductComponent', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_product_component_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticProductComponent(db.Model):
    plastic_product_component_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component.id'), primary_key=True)
    plastic_product_component = db.relationship('PlasticProductComponent', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_product_component_approved', lazy=True)
