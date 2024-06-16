from dataclasses import dataclass
import datetime


def collect_data(total, obj, key, sign, date_from=None, date_to=None):
    details = [
        detail 
        for detail in getattr(obj, f"{key}_details")  
        if (getattr(detail, key).submitted 
            and not getattr(detail, key).cancelled)
        ]

    for detail in details:
        record_date = getattr(detail, key).record_date

        if date_from and not date_to:
            if record_date < date_from:
                quantity = detail.quantity
                if sign:
                    total += quantity
                else:
                    total -= quantity
        else:
            if (record_date >= date_from) and (record_date <= date_to):
                quantity = detail.quantity
                if sign:
                    total += quantity
                else:
                    total -= quantity
    return total


@dataclass
class Inventory:
    obj: any
    date_from: str
    date_to: str

    @property
    def beginning(self):
        total = 0

        modules = {
            "raw_material_receipt": 1,
            "raw_material_issued": -1,
            "raw_material_adjustment": 1,
        }

        for key, sign in modules.items():        
            total = collect_data(total, self.obj, key, sign, self.date_from)

        return total
    
    @property
    def formatted_beginning(self):
        print("Beginning", self.beginning)
        return "{:,.2f}".format(self.beginning)
    
    @property
    def add(self):
        key = "raw_material_receipt"
        sign = 1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def formatted_add(self):
        return "{:,.2f}".format(self.add)
    
    @property
    def deduct(self):
        key = "raw_material_issued"
        sign = -1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def formatted_deduct(self):
        return "{:,.2f}".format(self.deduct)
    
    @property
    def adjustment(self):
        key = "raw_material_adjustment"
        sign = 1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def formatted_adjustment(self):
        return "{:,.2f}".format(self.adjustment)
    
    @property
    def ending(self):
        return self.beginning + self.add + self.deduct + self.adjustment

    @property
    def formatted_ending(self):
        return "{:,.2f}".format(self.ending)
    
    @property
    def ordered(self):
        key = "raw_material_request"
        sign = 1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def formatted_ordered(self):
        return "{:,.2f}".format(self.ordered)
    
    @property
    def total(self):
        return self.ending + self.ordered

    @property
    def formatted_total(self):
        return "{:,.2f}".format(self.total)
