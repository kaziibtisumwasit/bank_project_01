from django.db import models
from django.contrib.auth.models import User ## Django builtin User Model
from .constants import ACCOUNT_TYPE,GENDER_TYPE
# Create your models here.

# by default built in User models gives use username,password,email,firstname,lastname
# ei User model er shate baki fields ghual add korar jonno UserBankAccount model er shate oneToone relation builtup korechi


## django Builtin model -> User model er shate one to one relation builtup korechi , karon ekta user er ekta account thakbe
## User model gives us -> First name,last name ,username,password,email etc. but baki fields gular jonno amra UserBankAccount model er shate one to one relation builtup korechi
class UserBankAccount(models.Model):
    user = models.OneToOneField(User,related_name='account',on_delete=models.CASCADE) ## Ei related_name diye User model er elements ghula ke access korte parbo
    account_type = models.CharField(max_length=10 , choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True) ## account number always unique hobe , duplicate account number dile error show korbe
    birth_date = models.DateField(null=True,blank=True)
    gender =models.CharField(max_length=10,choices=GENDER_TYPE)
    initail_deposite_date = models.DateField(auto_now=True) # Jokhon account create hobe tokhon ei date ta automatically set hoye jabe.auto_now = True mane holo current date time
    balance = models.DecimalField(default=0,max_digits=12,decimal_places=2) # decimal_place => mane holo doshomik er pore 2 ghor ,
    #user can store 12 digit amount or money,When user create this account by default its set balance zero
    
    def __str__(self):
        return f"{self.user.username } -- AC: {self.account_no}"
    
# one user has one address so User er shate address er OneToOne relation
## Ekjon user er ektai information thkabe like username , address ,account thats why one to one relationship
class UserAddress(models.Model):
    user = models.OneToOneField(User,related_name='address',on_delete=models.CASCADE)# address use kore jeno user ke access korte pari
    street_address = models.CharField(max_length=100)
    city  = models.CharField(max_length=50)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.user.username} -- AC: {self.user.account.account_no}"
    ##ei model theke --> user model e gelam (User) use kore -->> User model theke UserBankAccount model e gelam
    ## Related_name (account ) er maddhome..
    
    
    
    
