
import re
from wtforms import ValidationError


def password_check(form, field):

    if len((field.data)) < 8:
        raise ValidationError("Your password length must be at least 8")
    elif re.search('[0-9]', field.data) is None:
        raise ValidationError("Your password myst have at least one number")
    elif re.search('[A-Z]', field.data) is None:
        raise ValidationError("Your password must have at least one capital letter")


