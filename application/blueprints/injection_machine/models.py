from application.extensions import db


class InjectionMachine(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    injection_machine_name = db.Column(db.String(255))
    injection_machine_code = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return self.injection_machine_name
    
    @property
    def preparer(self):
        user_prepare = UserInjectionMachine.query.filter(UserInjectionMachine.injection_machine_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminInjectionMachine.query.filter(AdminInjectionMachine.injection_machine_id==self.id).first()
        return admin_approve


class UserInjectionMachine(db.Model):
    injection_machine_id = db.Column(db.Integer, db.ForeignKey('injection_machine.id'), primary_key=True)
    injection_machine = db.relationship('InjectionMachine', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='injection_machine_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminInjectionMachine(db.Model):
    injection_machine_id = db.Column(db.Integer, db.ForeignKey('injection_machine.id'), primary_key=True)
    injection_machine = db.relationship('InjectionMachine', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='injection_machine_approved', lazy=True)
