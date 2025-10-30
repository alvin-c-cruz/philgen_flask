from application.extensions import db


class Measure(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    measure_name = db.Column(db.String(255))

    def __str__(self):
        return self.measure_name
    
    @property
    def preparer(self):
        user_prepare = UserMeasure.query.filter(UserMeasure.measure_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminMeasure.query.filter(AdminMeasure.measure_id==self.id).first()
        return admin_approve


class UserMeasure(db.Model):
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), primary_key=True)
    measure = db.relationship('Measure', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='measure_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminMeasure(db.Model):
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), primary_key=True)
    measure = db.relationship('Measure', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='measure_approved', lazy=True)
