from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime, timedelta
from flask_login import LoginManager
from dataclasses import dataclass
from flask import url_for

db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()


def month_first_day():
    date_today = datetime.today()
    year = date_today.year
    month = date_today.month
    day = 1
    first_day = str(datetime(year, month, day))[:10]

    return first_day


def month_last_day():
    date_today = datetime.today()
    year = date_today.year
    month = date_today.month
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    day = 1

    first_day_of_next_month = datetime(year, month, day)
    last_day = first_day_of_next_month - timedelta(days=1)
    last_day = str(last_day)[:10]

    return last_day


def incrementer(data):
    if not data:
        return 1

    if type(data) is int:
        return data + 1

    if data.isdigit():
        return str(int(data) + 1).rjust(len(data), '0')

    # Upon passing this line the data passed is alphanumeric combination
    reversed_data = data[::-1]
    reversed_number = ""
    for i in reversed_data:
        if i.isdigit():
            reversed_number += i
        else:
            break
    proper_number = reversed_number[::-1]

    if proper_number:
        return data[:len(data) - len(proper_number)] + str(int(proper_number) + 1).rjust(
            len(proper_number), '0')
    else:
        return data + "1"
    

def next_control_number(obj, control_number_field, record_date=None):
    def extract_numbers_from_right(s):
        numbers = ''
        non_numeric_encountered = False
        
        # Traverse the string in reverse
        for char in reversed(s):
            if char.isdigit():
                numbers = char + numbers
            else:
                non_numeric_encountered = True
                break
        
        # If no numbers were found or non-numeric characters encountered,
        # increment the last found number by 1 and return the modified string
        if not numbers or non_numeric_encountered:
            if numbers:
                # Calculate the new incremented number as a string
                incremented_number = str(int(numbers) + 1)
            else:
                incremented_number = '1'
            # Return the original string up to the point where numbers were found
            # concatenated with the incremented number, padded with leading zeros
            return s[:-len(numbers)] + incremented_number.zfill(len(numbers))
        
        # If only numbers were found, return the extracted number
        return numbers
    
    record = obj.query.order_by(getattr(obj, control_number_field).desc()).first()
    
    if not record:
        if record_date:
            year = record_date[2:4]
            month = record_date[5:7]
            return f"{year}-{month}-001"
        else:
            return "001"

    last_number = getattr(record, control_number_field)
    
    if record_date:
        prefix = last_number[:6]  # Assuming the format is "YY-MM-NNN"
        suffix = int(last_number[-3:])
        next_suffix = suffix + 2
        return f"{prefix}{next_suffix:03d}"
    else:
        # Extract numeric part and increment using the extracted function
        return incrementer(last_number)


def short_date(str_date):
    dte_date = datetime.strptime(str_date, "%Y-%m-%d")
    dte_date = datetime.strftime(dte_date, "%d-%b-%Y")
    return dte_date


@dataclass
class Url:
    object: any

    @property
    def home(self):
        return url_for(f"{self.object.__tablename__}.home")

    @property
    def add(self):
        return url_for(f"{self.object.__tablename__}.add")
    
    @property
    def edit(self):
        return url_for(f"{self.object.__tablename__}.edit", record_id=self.object.id)
    
    @property
    def delete(self):
        return url_for(f"{self.object.__tablename__}.delete", record_id=self.object.id)
    
    @property
    def view(self):
        return url_for(f"{self.object.__tablename__}.view", record_id=self.object.id)
    
    @property
    def cancel(self):
        return url_for(f"{self.object.__tablename__}.cancel", record_id=self.object.id)
    
    @property
    def unlock(self):
        return url_for(f"{self.object.__tablename__}.unlock", record_id=self.object.id)
    
    @property
    def print(self):
        return url_for(f"{self.object.__tablename__}.print", record_id=self.object.id)
    
