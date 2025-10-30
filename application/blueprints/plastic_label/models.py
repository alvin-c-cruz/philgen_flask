from application.extensions import db


class PlasticLabel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    label_name = db.Column(db.String(255))
    label_code = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.label_name
    
    @property
    def preparer(self):
        user_prepare = UserPlasticLabel.query.filter(UserPlasticLabel.plastic_label_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminPlasticLabel.query.filter(AdminPlasticLabel.plastic_label_id==self.id).first()
        return admin_approve


class UserPlasticLabel(db.Model):
    plastic_label_id = db.Column(db.Integer, db.ForeignKey('plastic_label.id'), primary_key=True)
    plastic_label = db.relationship('PlasticLabel', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_label_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticLabel(db.Model):
    plastic_label_id = db.Column(db.Integer, db.ForeignKey('plastic_label.id'), primary_key=True)
    plastic_label = db.relationship('PlasticLabel', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_label_approved', lazy=True)
