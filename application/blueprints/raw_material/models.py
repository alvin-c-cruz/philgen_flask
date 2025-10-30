from application.extensions import db


class RawMaterial(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    raw_material_name = db.Column(db.String(255))

    def __str__(self):
        return self.raw_material_name

    @property
    def preparer(self):
        return UserRawMaterial.query.filter(UserRawMaterial.raw_material_id==self.id).first()


class UserRawMaterial(db.Model):
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), primary_key=True)
    raw_material = db.relationship('RawMaterial', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='raw_material_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminRawMaterial(db.Model):
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), primary_key=True)
    raw_material = db.relationship('RawMaterial', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='raw_material_approved', lazy=True)
