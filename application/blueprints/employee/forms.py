from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Employee as Obj
from .models import UserEmployee as Preparer
from .models import AdminEmployee as Approver


@dataclass
class Form:
    id: int = None
    last_name: str = ""
    first_name: str = ""
    middle_name: str = ""
    birth_date: str = ""
    permanent_address: str = ""
    city_address: str = ""
    date_probationary: str = ""
    date_regular: str = ""
    employee_number: str = ""
    tin: str = ""
    sss_number: str = ""
    phic_number: str = ""
    hdmf_number: str = ""
    contact_number: str = ""
    email_address: str = ""
    contact_person_name: str = ""
    contact_person_relationship: str = ""
    contact_person_number: str = ""
    contact_person_address: str = ""
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def populate(self, object):
        self.id = object.id
        self.last_name = object.last_name
        self.first_name = object.first_name
        self.middle_name = object.middle_name
        self.birth_date = object.birth_date
        self.permanent_address = object.permanent_address
        self.city_address = object.city_address
        self.date_probationary = object.date_probationary
        self.date_regular = object.date_regular
        self.employee_number = object.employee_number
        self.tin = object.tin
        self.sss_number = object.sss_number
        self.phic_number = object.phic_number
        self.hdmf_number = object.hdmf_number
        self.contact_number = object.contact_number
        self.email_address = object.email_address
        self.contact_person_name = object.contact_person_name
        self.contact_person_relationship = object.contact_person_relationship
        self.contact_person_number = object.contact_person_number
        self.contact_person_address = object.contact_person_address

    def save(self):
        if self.id is None:
            # Add a new record
            record = Obj(
                last_name=self.last_name,
                first_name=self.first_name,
                middle_name=self.middle_name,
                birth_date=self.birth_date,
                permanent_address=self.permanent_address,
                city_address=self.city_address,
                date_probationary=self.date_probationary,
                date_regular=self.date_regular,
                employee_number=self.employee_number,
                tin=self.tin,
                sss_number=self.sss_number,
                phic_number=self.phic_number,
                hdmf_number=self.hdmf_number,
                contact_number=self.contact_number,
                email_address=self.email_address,
                contact_person_name=self.contact_person_name,
                contact_person_relationship=self.contact_person_relationship,
                contact_person_number=self.contact_person_number,
                contact_person_address=self.contact_person_address,
                )
    
            db.session.add(record)
            db.session.commit()

            preparer = Preparer(
                employee_id=record.id,
                user_id=self.user_prepare_id
            )

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            preparer = Preparer.query.filter_by(employee_id=self.id).first()

            if record:
                record.last_name = self.last_name
                record.first_name = self.first_name
                record.middle_name = self.middle_name
                record.birth_date = self.birth_date
                record.permanent_address = self.permanent_address
                record.city_address = self.city_address
                record.date_probationary = self.date_probationary
                record.date_regular = self.date_regular
                record.employee_number = self.employee_number
                record.tin = self.tin
                record.sss_number = self.sss_number
                record.phic_number = self.phic_number
                record.hdmf_number = self.hdmf_number
                record.contact_number = self.contact_number
                record.email_address = self.email_address
                record.contact_person_name = self.contact_person_name
                record.contact_person_relationship = self.contact_person_relationship
                record.contact_person_number = self.contact_person_number
                record.contact_person_address = self.contact_person_address

                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def post(self, request_form):
        self.id = request_form.get('record_id')
        self.last_name = request_form.get('last_name')
        self.first_name = request_form.get('first_name')
        self.middle_name = request_form.get('middle_name')
        self.birth_date = request_form.get('birth_date')
        self.permanent_address = request_form.get('permanent_address')
        self.city_address = request_form.get('city_address')
        self.date_probationary = request_form.get('date_probationary')
        self.date_regular = request_form.get('date_regular')
        self.employee_number = request_form.get('employee_number')
        self.tin = request_form.get('tin')
        self.sss_number = request_form.get('sss_number')
        self.phic_number = request_form.get('phic_number')
        self.hdmf_number = request_form.get('hdmf_number')
        self.contact_number = request_form.get('contact_number')
        self.email_address = request_form.get('email_address')
        self.contact_person_name = request_form.get('contact_person_name')
        self.contact_person_relationship = request_form.get('contact_person_relationship')
        self.contact_person_number = request_form.get('contact_person_number')
        self.contact_person_address = request_form.get('contact_person_address')

    def validate_on_submit(self):
        self.errors = {}

        if not self.last_name:
            self.errors["last_name"] = "Please type last name."
            
        if not self.first_name:
            self.errors["first_name"] = "Please type first name."
            
            
        if self.last_name and self.first_name:
            existing_ = Obj.query.filter(
                func.lower(Obj.last_name) == func.lower(self.last_name),
                func.lower(Obj.middle_name) == func.lower(self.middle_name),
                func.lower(Obj.first_name) == func.lower(self.first_name),
                Obj.id != self.id
                ).first()
            if existing_:
                self.errors["last_name"] = "Employee already exists."


        if not self.errors:
            return True
        else:
            return False    
