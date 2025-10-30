from application.extensions import db


class PlasticLabelStatus(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    plastic_label_status_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.plastic_label_status_name
    
    def __repr__(self) -> str:
        return self.plastic_label_status_name
    
    @property
    def preparer(self):
        user_prepare = UserPlasticLabelStatus.query.filter(UserPlasticLabelStatus.plastic_label_status_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminPlasticLabelStatus.query.filter(AdminPlasticLabelStatus.plastic_label_status_id==self.id).first()
        return admin_approve


class UserPlasticLabelStatus(db.Model):
    plastic_label_status_id = db.Column(db.Integer, db.ForeignKey('plastic_label_status.id'), primary_key=True)
    plastic_label_status = db.relationship('PlasticLabelStatus', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_label_status_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticLabelStatus(db.Model):
    plastic_label_status_id = db.Column(db.Integer, db.ForeignKey('plastic_label_status.id'), primary_key=True)
    plastic_label_status = db.relationship('PlasticLabelStatus', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_label_status_approved', lazy=True)
