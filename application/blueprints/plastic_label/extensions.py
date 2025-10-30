from dataclasses import dataclass
import datetime


@dataclass
class Inventory:
    label: any
    date_from: str
    date_to: str

    @property
    def beginning(self):
        total = 0

        # Receipt
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_receipt_details 
            if (label_detail.plastic_label_receipt.submitted 
                and not label_detail.plastic_label_receipt.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_label_receipt.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total += quantity

        # Issuance
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_issuance_details 
            if (label_detail.plastic_label_issuance.submitted 
                and not label_detail.plastic_label_issuance.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_label_issuance.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total -= quantity

        # Return
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_return_details 
            if (label_detail.plastic_label_return.submitted 
                and not label_detail.plastic_label_return.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_label_return.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total += quantity

        # Returned Defectives
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_return_details 
            if (label_detail.plastic_label_return.submitted 
                and not label_detail.plastic_label_return.cancelled
                and not label_detail.plastic_label_status.plastic_label_status_name == "GOOD"
                and label_detail.plastic_label_status
                )
                ]
        for detail in details:
            record_date = detail.plastic_label_return.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total -= quantity

        # Adjustment
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_adjustment_details 
            if (label_detail.plastic_label_adjustment.submitted 
                and not label_detail.plastic_label_adjustment.cancelled)
                ]
        for detail in details:
            record_date = detail.plastic_label_adjustment.record_date
            if record_date < self.date_from:
                quantity = detail.quantity
                total += quantity

        return total

    @property
    def received(self):
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_receipt_details 
            if (label_detail.plastic_label_receipt.submitted 
                and not label_detail.plastic_label_receipt.cancelled)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_label_receipt.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total += quantity

        return total
    
    @property
    def returned(self):
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_return_details 
            if (label_detail.plastic_label_return.submitted 
                and not label_detail.plastic_label_return.cancelled)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_label_return.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total += quantity

        return total
    
    @property
    def defective(self):
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_return_details 
            if (label_detail.plastic_label_return.submitted 
                and not label_detail.plastic_label_return.cancelled)
                ]
        total = 0
        for detail in details:
            if detail.plastic_label_status.plastic_label_status_name == "GOOD": continue
            record_date = detail.plastic_label_return.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total -= quantity

        return total
    
    @property
    def issued(self):
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_issuance_details 
            if (label_detail.plastic_label_issuance.submitted 
                and not label_detail.plastic_label_issuance.cancelled)
                ]
        
        total = 0
        for detail in details:
            record_date = detail.plastic_label_issuance.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total -= quantity

        return total
    
    @property
    def adjustment(self):
        details = [
            label_detail 
            for label_detail in self.label.plastic_label_adjustment_details 
            if (label_detail.plastic_label_adjustment.submitted 
                and not label_detail.plastic_label_adjustment.cancelled)
                ]
        total = 0
        for detail in details:
            record_date = detail.plastic_label_adjustment.record_date
            if (record_date >= self.date_from) and (record_date <= self.date_to):
                quantity = detail.quantity
                total += quantity

        return total
    
    
    @property
    def ending(self):
        return self.beginning + self.received + self.returned + self.issued + self.defective + self.adjustment

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

    @property
    def formatted_average(self):
        average = 100
        return "{0:,.2}".format(average)

