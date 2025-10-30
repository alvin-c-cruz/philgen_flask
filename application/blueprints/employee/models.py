from application.extensions import db


class Employee(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    last_name = db.Column(db.String())
    first_name = db.Column(db.String())
    middle_name = db.Column(db.String())
    birth_date = db.Column(db.String())
    permanent_address = db.Column(db.String())
    city_address = db.Column(db.String())
    date_probationary = db.Column(db.String())
    date_regular = db.Column(db.String())
    employee_number = db.Column(db.String())
    tin = db.Column(db.String())
    sss_number = db.Column(db.String())
    phic_number = db.Column(db.String())
    hdmf_number = db.Column(db.String())
    contact_number = db.Column(db.String())
    email_address = db.Column(db.String())
    contact_person_name = db.Column(db.String())
    contact_person_relationship = db.Column(db.String())
    contact_person_number = db.Column(db.String())
    contact_person_address = db.Column(db.String())
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def preparer(self):
        user_prepare = UserEmployee.query.filter(UserEmployee.employee_id==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminEmployee.query.filter(AdminEmployee.employee_id==self.id).first()
        return admin_approve


class UserEmployee(db.Model):
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), primary_key=True)
    employee = db.relationship('Employee', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='employee_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminEmployee(db.Model):
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), primary_key=True)
    employee = db.relationship('Employee', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='employee_approved', lazy=True)
