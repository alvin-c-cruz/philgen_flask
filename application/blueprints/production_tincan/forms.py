from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import ProductionTincan as Obj, ProductionTincanDetail as Details, UserProductionTincan as Preparer
from datetime import datetime


from .. product.models import Product

DETAIL_ROWS = 10


@dataclass
class SubForm:
    id: int = 0
    production_tincan_id:int = 0
    quantity: float = 0
    measure_id: int = 0
    product_id: int = 0
    side_note: str = ""
    
    product_name: str = ""

    errors = {}

    def populate(self, row):
        self.id = row.id
        self.production_tincan_id = row.production_tincan_id
        self.quantity = row.quantity
        self.measure_id = row.measure_id
        self.product_id = row.product_id
        self.product_name = row.product.product_name
        self.side_note = row.side_note 

    def validate(self):
        self.errors = {}

        if self.is_dirty():
            if self.quantity <= 0:
                self.errors["quantity"] = "Quantity should be greater than zero (0)."

            if not self.measure_id:
                self.errors["measure_id"] = "Please select measure."

            if not self.product_name:
                self.errors["product_name"] = "Please type item."
            else:
                product = Product.query.filter(Product.product_name==self.product_name).first()
                if not product:
                    self.errors["product_name"] = f"{self.product_name} does not exists."

        if not self.errors:
            return True
        else:
            return False    

    def is_dirty(self):
        return any([
            self.quantity, 
            self.measure_id, 
            self.product_id, 
            self.product_name,
            self.side_note
            ])    
        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    product_number: str = ""
    notes: str = ""
    submitted: str = ""
    cancelled: str = ""
    prepared_by: str = ""
    approved_by: str = ""
    locked: bool = False

    user_prepare_id: int = None


    details = []
    errors = {}

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def save(self):
        if self.id is None:
            # Add a new record
            new_record = Obj(
                record_date=self.record_date,
                production_number=self.production_number,
                notes=self.notes,
                submitted=self.submitted,
                prepared_by=self.prepared_by,
                approved_by=self.approved_by,
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail.is_dirty():
                    new_detail = Details(
                        production_tincan_id=new_record.id,
                        quantity=detail.quantity,
                        measure_id=detail.measure_id,
                        product_id=detail.product_id,
                        side_note=detail.side_note                    
                    )
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(
                production_tincan_id=new_record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(production_tincan_id=self.id).first()
                preparer.user_id = self.user_prepare_id

                record.record_date = self.record_date
                record.production_number = self.production_number
                record.notes = self.notes
                record.submitted = self.submitted
                record.prepared_by = self.prepared_by
                record.approved_by = self.approved_by
                
                details = Details.query.filter(Details.production_tincan_id==self.id)
                for detail in details:
                    db.session.delete(detail)

                for _, detail in self.details:
                    if detail.is_dirty():
                        row_detail = Details(
                            production_tincan_id=record.id,
                            quantity=detail.quantity,
                            measure_id=detail.measure_id,
                            product_id=detail.product_id,
                            side_note=detail.side_note
                            )
                        db.session.add(row_detail)  
                
        db.session.commit()
   
    def populate(self, obj):
        self.id = obj.id
        self.record_date = obj.record_date
        self.production_number = obj.production_number
        self.notes = obj.notes
        self.prepared_by = obj.prepared_by
        self.approved_by = obj.approved_by
        self.submitted = obj.submitted
        self.cancelled = obj.cancelled

        for i, row in enumerate(obj.production_tincan_details):
            subform = SubForm()
            subform.populate(row)
            self.details[i] = (i, subform)

    def post(self, request_form):
        self.id = request_form.get('record_id')
        self.record_date = request_form.get('record_date')
        self.production_number = request_form.get('production_number')
        self.notes = request_form.get('notes')
        self.prepared_by = request_form.get('prepared_by')
        self.approved_by = request_form.get('approved_by')

        for i in range(DETAIL_ROWS):
            if type(request_form.get(f'quantity-{i}')) == str:
                quantity_value = request_form.get(f'quantity-{i}')
                if quantity_value.isnumeric() or (quantity_value.replace('.', '', 1).isdigit() and quantity_value.count('.') <= 1):
                    self.details[i][1].quantity = float(quantity_value)
                else:
                    self.details[i][1].quantity = 0
            else: 
                self.details[i][1].quantity = request_form.get(f'quantity-{i}')

            self.details[i][1].measure_id = int(request_form.get(f'measure_id-{i}'))

            product_name = request_form.get(f'product_name-{i}')
            self.details[i][1].product_name = product_name
            
            product = Product.query.filter_by(product_name=product_name).first()
            if product:
                self.details[i][1].product_id = product.id
                
            self.details[i][1].side_note = request_form.get(f'side_note-{i}')

    def validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.production_number:
            self.errors["production_number"] = "Please type reference number."
        else:
            duplicate = Obj.query.filter(func.lower(Obj.production_number) == func.lower(self.production_number), Obj.id != self.id).first()
            if duplicate:
                self.errors["production_number"] = "Reference is already used, please verify."        


        for i in range(DETAIL_ROWS):
            if not self.details[i][1].validate():
                detail_validation = False

        all_not_dirty = True
        for _, detail in self.details:
            if detail.is_dirty():
                all_not_dirty = False

        if all_not_dirty:
            self.errors["entry"] = "There should be at least one entry."       

        if not self.errors and detail_validation:
            return True        
    
    def submit(self):
        self.submitted = str(datetime.today())[:10]

    @property
    def locked_(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
    