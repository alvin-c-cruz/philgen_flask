from application.extensions import db


class PlasticRawMaterial(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    plastic_raw_material_name = db.Column(db.String(255))
    plastic_raw_material_code = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.plastic_raw_material_name
    
    @property
    def preparer(self):
        user_prepare = UserPlasticRawMaterial.query.filter(UserPlasticRawMaterial.plastic_raw_material_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminPlasticRawMaterial.query.filter(AdminPlasticRawMaterial.plastic_raw_material_id==self.id).first()
        return admin_approve


class UserPlasticRawMaterial(db.Model):
    plastic_raw_material_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material.id'), primary_key=True)
    plastic_raw_material = db.relationship('PlasticRawMaterial', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_raw_material_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticRawMaterial(db.Model):
    plastic_raw_material_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material.id'), primary_key=True)
    plastic_raw_material = db.relationship('PlasticRawMaterial', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_raw_material_approved', lazy=True)
