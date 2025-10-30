from application.extensions import db, short_date
import datetime


class PlasticProductComponentProduction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    plastic_product_component_production_number = db.Column(db.String())

    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=False)
    shift = db.relationship('Shift', backref='plastic_product_component_productions', lazy=True)

    injection_machine_id = db.Column(db.Integer, db.ForeignKey('injection_machine.id'), nullable=False)
    injection_machine = db.relationship('InjectionMachine', backref='plastic_product_component_productions', lazy=True)

    # actual_cycle_time = db.Column(db.String())


    notes = db.Column(db.String())

    active = db.Column(db.Boolean())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def __str__(self):
        return f"{self.plastic_product_component_production_number}"

    @property
    def preparer(self):
        obj = UserPlasticProductComponentProduction.query.filter(UserPlasticProductComponentProduction.plastic_product_component_production_id==self.id).first()
        return obj

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None

    @property
    def formatted_submitted(self):
        return short_date(self.submitted) if self.submitted else None

    @property
    def formatted_cancelled(self):
        return short_date(self.cancelled) if self.cancelled else None
    
    def is_submitted(self):
        return True if self.submitted else False


class PlasticProductComponentProductionDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    plastic_product_component_production_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component_production.id'), nullable=False)
    plastic_product_component_production = db.relationship('PlasticProductComponentProduction', backref='plastic_product_component_production_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='plastic_product_component_production_details', lazy=True)

    plastic_product_component_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component.id'), nullable=False)
    plastic_product_component = db.relationship('PlasticProductComponent', backref='plastic_product_component_production_details', lazy=True)

    plastic_product_component_status_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component_status.id'), nullable=False)
    plastic_product_component_status = db.relationship('PlasticProductComponentStatus', backref='plastic_product_component_production_details', lazy=True)

    side_note = db.Column(db.String())


class UserPlasticProductComponentProduction(db.Model):
    plastic_product_component_production_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component_production.id'), primary_key=True)
    plastic_product_component_production = db.relationship('PlasticProductComponentProduction', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_product_component_production_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticProductComponentProduction(db.Model):
    plastic_product_component_production_id = db.Column(db.Integer, db.ForeignKey('plastic_product_component_production.id'), primary_key=True)
    plastic_product_component_production = db.relationship('PlasticProductComponentProduction', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_product_component_production_approved', lazy=True)

