from application.extensions import db


class Department(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    department_name = db.Column(db.String(255))

    def __str__(self):
        return self.department_name
    
    @property
    def preparer(self):
        user_measure = UserDepartment.query.filter(UserDepartment.department_id==self.id).first()
        return user_measure
    
    @property
    def approved(self):
        admin_approve = AdminDepartment.query.filter(AdminDepartment.department_id==self.id).first()
        return admin_approve


class UserDepartment(db.Model):
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), primary_key=True)
    department = db.relationship('Department', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='department_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminDepartment(db.Model):
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), primary_key=True)
    department = db.relationship('Department', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='department_approved', lazy=True)
