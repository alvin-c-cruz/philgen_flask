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
            "plastic_product_component_production": 1,
            "plastic_product_component_transmitted": -1,
            "plastic_product_component_returned": -1,
            "plastic_product_component_rejected": -1,
            "plastic_product_component_adjustment": 1
        }

        for key, sign in modules.items():        
            total = collect_data(total, self.obj, key, sign, self.date_from)
        
        return total

    @property
    def produced(self):
        key = "plastic_product_component_production"
        sign = 1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def transmitted(self):
        key = "plastic_product_component_transmitted"
        sign = -1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def returned(self):
        key = "plastic_product_component_returned"
        sign = -1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    @property
    def adjustment(self):
        key = "plastic_product_component_adjustment"
        sign = 1
        total = 0
        total = collect_data(total, self.obj, key, sign, self.date_from, self.date_to)

        return total
    
    
    @property
    def ending(self):
        return self.beginning + self.produced + self.transmitted + self.returned + self.adjustment

    @property
    def formatted_beginning(self):
        return "{0:,}".format(self.beginning)
    
    @property
    def formatted_produced(self):
        return "{0:,}".format(self.produced)
    
    @property
    def formatted_transmitted(self):
        return "{0:,}".format(self.transmitted)
    
    @property
    def formatted_returned(self):
        return "{0:,}".format(self.returned)
    
    @property
    def formatted_adjustment(self):
        return "{0:,}".format(self.adjustment)
    
    @property
    def formatted_ending(self):
        return "{0:,}".format(self.ending)

