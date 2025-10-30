from application.extensions import db, short_date, long_date
import datetime
from collections import defaultdict


class ReceivingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())
    receiving_report_number = db.Column(db.String())

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = db.relationship('Vendor', backref='receiving_reports', lazy=True)

    supporting_documents = db.Column(db.String())

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    received_by = db.Column(db.String())
    prepared_by = db.Column(db.String())
    checked_by = db.Column(db.String())

    @property
    def preparer(self):
        obj = UserReceivingReport.query.filter(UserReceivingReport.receiving_report_id==self.id).first()
        return obj

    @property
    def formatted_voucher_date(self):
        return long_date(self.record_date) if self.record_date else None

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None

    @property
    def formatted_submitted(self):
        return short_date(self.submitted) if self.submitted else None

    @property
    def formatted_cancelled(self):
        return short_date(self.cancelled) if self.cancelled else None

    @property
    def purchase_order_numbers(self):
        results = []
        for detail in self.receiving_report_details:
            results.append(detail.purchase_order_number)
            
        return ', '.join(sorted(set(results)))
    

class ReceivingReportDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    purchase_order_number = db.Column(db.String())

    receiving_report_id = db.Column(db.Integer, db.ForeignKey('receiving_report.id'), nullable=False)
    receiving_report = db.relationship('ReceivingReport', backref='receiving_report_details', lazy=True)

    quantity = db.Column(db.Float, default=0)
    
    measure_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure = db.relationship('Measure', backref='receiving_report_details', lazy=True)

    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    raw_material = db.relationship('RawMaterial', backref='receiving_report_details', lazy=True)

    @property
    def formatted_quantity(self):
        # Convert to string with enough precision to catch all decimals
        qty_str = f'{self.quantity:.10f}'.rstrip('0').rstrip('.')  # remove trailing zeros and dot if needed
        
        if '.' in qty_str:
            decimals = len(qty_str.split('.')[1])
        else:
            decimals = 0
        
        # Cap decimals to a max (e.g., 4)
        max_decimals = 4
        decimals = min(decimals, max_decimals)

        fmt = f'{{:,.{decimals}f}}'
        return fmt.format(self.quantity)
    
    
class UserReceivingReport(db.Model):
    receiving_report_id = db.Column(db.Integer, db.ForeignKey('receiving_report.id'), primary_key=True)
    receiving_report = db.relationship('ReceivingReport', backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='receiving_report_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminReceivingReport(db.Model):
    receiving_report_id = db.Column(db.Integer, db.ForeignKey('receiving_report.id'), primary_key=True)
    receiving_report = db.relationship('ReceivingReport', backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref='receiving_report_approved', lazy=True)
