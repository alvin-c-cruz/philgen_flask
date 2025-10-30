from application.extensions import db


class PlasticRawMaterialStatus(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    plastic_raw_material_status_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.plastic_raw_material_status_name
    
    def __repr__(self) -> str:
        return self.plastic_raw_material_status_name
    
    @property
    def preparer(self):
        user_prepare = UserPlasticRawMaterialStatus.query.filter(UserPlasticRawMaterialStatus.plastic_raw_material_status_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminPlasticRawMaterialStatus.query.filter(AdminPlasticRawMaterialStatus.plastic_raw_material_status_id==self.id).first()
        return admin_approve


class UserPlasticRawMaterialStatus(db.Model):
    plastic_raw_material_status_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material_status.id'), primary_key=True)
    plastic_raw_material_status = db.relationship('PlasticRawMaterialStatus', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_raw_material_status_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticRawMaterialStatus(db.Model):
    plastic_raw_material_status_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material_status.id'), primary_key=True)
    plastic_raw_material_status = db.relationship('PlasticRawMaterialStatus', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_raw_material_status_approved', lazy=True)
