from application.extensions import db


class Operator(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    last_name = db.Column(db.String())
    first_name = db.Column(db.String())
    middle_name = db.Column(db.String())
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def preparer(self):
        user_prepare = UserOperator.query.filter(UserOperator.operator_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminOperator.query.filter(AdminOperator.operator_id==self.id).first()
        return admin_approve


class UserOperator(db.Model):
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'), primary_key=True)
    operator = db.relationship('Operator', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='operator_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminOperator(db.Model):
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'), primary_key=True)
    operator = db.relationship('Operator', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='operator_approved', lazy=True)
