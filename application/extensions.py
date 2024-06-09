from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime, timedelta
from flask_login import LoginManager

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


def next_control_number(obj, control_number_field, record_date=None):
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
        prefix = last_number[:6]
        suffix = int(last_number[-3:]) + 1
        suffix = '{:03d}'.format(suffix)

        return f"{prefix}{suffix}"
    else:
        length = len(last_number)
        suffix = int(last_number) + 1
        string_format = '{:0' + str(length) + 'd}'
        suffix = string_format.format(suffix)

        return suffix


def short_date(str_date):
    dte_date = datetime.strptime(str_date, "%Y-%m-%d")
    dte_date = datetime.strftime(dte_date, "%d-%b-%Y")
    return dte_date
