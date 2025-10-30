from application.extensions import db


class Lithography(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    lithography_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.lithography_name
    
    @property
    def preparer(self):
        user_prepare = UserLithography.query.filter(UserLithography.lithography_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminLithography.query.filter(AdminLithography.lithography_id==self.id).first()
        return admin_approve


class UserLithography(db.Model):
    lithography_id = db.Column(db.Integer, db.ForeignKey('lithography.id'), primary_key=True)
    lithography = db.relationship('Lithography', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='lithography_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminLithography(db.Model):
    lithography_id = db.Column(db.Integer, db.ForeignKey('lithography.id'), primary_key=True)
    lithography = db.relationship('Lithography', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='lithography_approved', lazy=True)
