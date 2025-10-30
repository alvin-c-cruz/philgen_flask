from application.extensions import db


class Shift(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    shift_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.shift_name
    
    @property
    def preparer(self):
        user_prepare = UserShift.query.filter(UserShift.shift_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminShift.query.filter(AdminShift.shift_id==self.id).first()
        return admin_approve


class UserShift(db.Model):
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), primary_key=True)
    shift = db.relationship('Shift', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='shift_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminShift(db.Model):
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), primary_key=True)
    shift = db.relationship('Shift', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='shift_approved', lazy=True)
