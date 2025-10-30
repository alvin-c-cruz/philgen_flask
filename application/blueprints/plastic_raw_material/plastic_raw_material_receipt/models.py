from application.extensions import db, short_date
import datetime


class PlasticRawMaterialReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    plastic_raw_material_receipt_number = db.Column(db.String())

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = db.relationship('Vendor', backref='plastic_raw_material_receipts', lazy=True)

    packing_list = db.Column(db.String())
    notes = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def __str__(self):
        return f"{self.plastic_raw_material_receipt_number}"

    @property
    def preparer(self):
        obj = UserPlasticRawMaterialReceipt.query.filter(UserPlasticRawMaterialReceipt.plastic_raw_material_receipt_id==self.id).first()
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


class PlasticRawMaterialReceiptDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    plastic_raw_material_receipt_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material_receipt.id'), nullable=False)
    plastic_raw_material_receipt = db.relationship('PlasticRawMaterialReceipt', backref='plastic_raw_material_receipt_details', lazy=True)


    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='plastic_raw_material_receipt_details', lazy=True)

    plastic_raw_material_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material.id'), nullable=False)
    plastic_raw_material = db.relationship('PlasticRawMaterial', backref='plastic_raw_material_receipt_details', lazy=True)

    side_note = db.Column(db.String())


class UserPlasticRawMaterialReceipt(db.Model):
    plastic_raw_material_receipt_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material_receipt.id'), primary_key=True)
    plastic_raw_material_receipt = db.relationship('PlasticRawMaterialReceipt', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_raw_material_receipt_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminPlasticRawMaterialReceipt(db.Model):
    plastic_raw_material_receipt_id = db.Column(db.Integer, db.ForeignKey('plastic_raw_material_receipt.id'), primary_key=True)
    plastic_raw_materialplastic_label_receipt = db.relationship('PlasticRawMaterialReceipt', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='plastic_raw_material_receipt_approved', lazy=True)
