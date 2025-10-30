from dataclasses import dataclass
import datetime


@dataclass
class Inventory:
    obj: any
    date_from: str
    date_to: str

    @property
    def beginning(self):
        total = 0

        # Receipt
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_receipt_details 
            if (detail.plastic_raw_material_receipt.submitted 
                and not detail.plastic_raw_material_receipt.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_raw_material_receipt.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total += quantity

        # Issuance
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_issuance_details 
            if (detail.plastic_raw_material_issuance.submitted 
                and not detail.plastic_raw_material_issuance.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_raw_material_issuance.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total -= quantity

        # Return
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_return_details 
            if (detail.plastic_raw_material_return.submitted 
                and not detail.plastic_raw_material_return.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_raw_material_return.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total += quantity

        # Returned Defectives
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_return_details 
            if (detail.plastic_raw_material_return.submitted 
                and not detail.plastic_raw_material_return.cancelled
                and not detail.plastic_raw_material_status == "Good"
                and detail.plastic_raw_material_status)
                ]
        for detail in details:
            record_date = detail.plastic_raw_material_return.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total -= quantity

        # Adjustment
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_adjustment_details 
            if (detail.plastic_raw_material_adjustment.submitted 
                and not detail.plastic_raw_material_adjustment.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_raw_material_adjustment.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total += quantity

        return total

    @property
    def received(self):
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_receipt_details 
            if (detail.plastic_raw_material_receipt.submitted 
                and not detail.plastic_raw_material_receipt.cancelled)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_raw_material_receipt.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total += quantity

        return total
    
    @property
    def returned(self):
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_return_details 
            if (detail.plastic_raw_material_return.submitted 
                and not detail.plastic_raw_material_return.cancelled)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_raw_material_return.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total += quantity

        return total
    
    @property
    def defective(self):
        details = [
            detail 
            for detail in self.plastic_raw_material_return.plastic_raw_material_return_details 
            if (detail.plastic_raw_material_return.submitted 
                and not detail.plastic_raw_material_return.cancelled
                and not detail.plastic_raw_material_status == "Good"
                and detail.plastic_raw_material_status)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_raw_material_return.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total -= quantity

        return total
    
    @property
    def issued(self):
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_issuance_details 
            if (detail.plastic_raw_material_issuance.submitted 
                and not detail.plastic_raw_material_issuance.cancelled)
                ]
        
        total = 0
        for detail in details:
            record_date = detail.plastic_raw_material_issuance.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total -= quantity

        return total
    
    @property
    def adjustment(self):
        details = [
            detail 
            for detail in self.obj.plastic_raw_material_adjustment_details 
            if (detail.plastic_raw_material_adjustment.submitted 
                and not detail.plastic_raw_material_adjustment.cancelled)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_raw_material_adjustment.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total += quantity

        return total
    
    
    @property
    def ending(self):
        return self.beginning + self.received + self.returned + self.issued + self.adjustment

    @property
    def formatted_beginning(self):
        return "{0:,}".format(self.beginning)
    
    @property
    def formatted_received(self):
        return "{0:,}".format(self.received)
    
    @property
    def formatted_returned(self):
        return "{0:,}".format(self.returned)
    
    @property
    def formatted_defective(self):
        return "{0:,}".format(self.defective)
    
    @property
    def formatted_issued(self):
        return "{0:,}".format(self.issued)
    
    @property
    def formatted_adjustment(self):
        return "{0:,}".format(self.adjustment)
    
    @property
    def formatted_ending(self):
        return "{0:,}".format(self.ending)

