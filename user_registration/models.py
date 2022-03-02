import uuid
from django.db import models

# Create your models here.

from django.contrib.auth.models import User,AbstractUser

class User(AbstractUser):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number= models.CharField(max_length=15, null=True)
    adhar_card_no = models.CharField(max_length=15, null=True)
    city = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=255, null=True)
    date_of_birth= models.DateField(null=True)
    gender = models.CharField(max_length=5, null=True)
    user_public_key = models.TextField(null=True)


"""
# import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

date_of_birth = date(1990, 8, 18) 
today_date = datetime.now().date()

datetime.strptime('24-05-2010', "%d-%m-%Y").date()

difference_in_years = relativedelta(today_date, date_of_birth).years
"""

"""
# generate random username
import random
def get_random_username(length=10, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))

# generate random password
password = User.objects.make_random_password(length=14)
"""



