from application.extensions import db


class PlasticProductComponentStatus(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    plastic_product_component_status_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.plastic_product_component_status_name
    
    @property
    def preparer(self):
        user_prepare = UserPlasticProductComponentStatus.query.filter(UserPlasticProductComponentStatus.plastic_product_component_status_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminPlasticProductComponentStatus.query.filter(AdminPlasticProductComponentStatus.plastic_product_component_status_id==self.id).first()
        return admin_approve


class UserPlasticProductComponentStatus(db.Model):
    plastic_product_component_status_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component_status.id'), primary_key=True)
    plastic_product_component_status = db.relationship('PlasticProductComponentStatus', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_product_component_status_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticProductComponentStatus(db.Model):
    plastic_product_component_status_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component_status.id'), primary_key=True)
    plastic_product_component_status = db.relationship('PlasticProductComponentStatus', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_product_component_status_approved', lazy=True)
