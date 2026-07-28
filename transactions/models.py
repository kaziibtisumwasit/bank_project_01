from django.db import models
from accounts.models import UserBankAccount 
from .constance import TRANSACTION_TYPE
class Transaction(models.Model):
    ##UserBankAccount.transaction diye Transaction model er data access korte parbo tai related name e transaction use korlam
    account = models.ForeignKey(UserBankAccount,related_name="transaction",on_delete=models.CASCADE) #
    ## Ekta account er multiple transaction hote pare tai ForeignKey use kora holo
    #UserBankAccount er shate one to many transation hobe.A use can transation multiple time
    amount = models.DecimalField(decimal_places=2,max_digits=12) ## je amount ta transaction hobe --> add or minus 
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12) ## Transaction er por user er account e koto taka thakbe seta store korbe
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE,null=True)
    time_stamp = models.DateTimeField(auto_now_add= True) ## current date time automatically set hobe jokhon user transaction korbe
    loan_approve = models.BooleanField(default= False) # by default user jolhon loan er jonno requesst korbe by defalut loan loan pending e thakbe
    
    
    class Meta:
        #Transition ta ke sort korbo date time er upor
        # Fileld gule ke ordering korte use hoi ordering function
        ordering = ['time_stamp']
        
        ##class Meta er kaj holo model er extra information add kora ba modification kora
        