from django import forms
from .models import Transaction

##Parent class form
class TransactionForms(forms.ModelForm): # Models er fields ke form er field e convert kore
    class Meta:
        model = Transaction
        fields =['amount' , 'transaction_type']
        
    
    #transaction_type field ta grayout hote  disable hoye thakbe , user ei field ta change korte parbe na
    ## jokhon ei form er object niye kaj korte hobe ba object te ke connected korte hobe tokhon ei kaj ta kora lagbe
    def __init__(self,*args,**kwargs):
        ## jokhon ei form er object create hobe tokhon account value ta pass korte hobe , karon account field ta form er moddhe nai
        self.account = kwargs.pop('account')  ## account ei same name e views er class method e access korte hobe
        super().__init__(*args,**kwargs) ## Django er built in form er __init__ method ke call korlam , overriding korar jonno super() use korlam
        self.fields['transaction_type'].disabled = True ## Ei field ta disable ba grayout dekhabe frontend e 
        self.fields['transaction_type'].widget= forms.HiddenInput() # user ei field ta dekhbe na , Hide kora thakbe
        
    def save(self,commit=True):
        self.instance.account = self.account ## current user er account 
        self.instance.balance_after_transaction = self.account.balance ## initailly koto taka rakhte chaitesi ba koto taka add korte chitesi
        return super().save() #save korlam
    
    
##TransactionForm Ke inherite korbo
##Model Er ammount field ke clean korte clean_amount builting function use korechi
## clean_field_name
## raise is a build in keyword for showing an error 
## form.ValidationError

## jokhon kono ekta form er field ke filter ba update ba clean korte chai tokhon clean_field_name method use hoi

class DepositForm(TransactionForms):
    #amount field er value ke clean korte & Conditions add korte clean_amount method use korlam
    def clean_amount(self):## builtin method
        min_diposit_amount = 100
        ##amount holo user je taka ta ei form e enter korsi ba je amount ta 
        amount = self.cleaned_data.get('amount') ##user deposite form er fillup kora form theke ei amount value ke nilam
        if amount < min_diposit_amount:
            ## raise holo error show korar keyword
            raise forms.ValidationError(
                f"Your Need To Deposit At Least {min_diposit_amount}"
            ) ## error ashle amount ta return hobe na just error show korbe
        return amount
    
class WithdrawForm(TransactionForms):
    def clean_amount(self):
        account = self.account ## current user account theke request ashche , oi account ti ke dhorlam
        min_withdraw = 500
        max_withdraw = 2000
        balance = account.balance   ##Transactions_model--> account field -->> UserBankAccount_model --> balanace field
        amount = self.cleaned_data.get('amount')## je amount ta form er field e enter korsi oi amount ta 
        
        if amount < min_withdraw:
            raise forms.ValidationError(
                f"You Can Withdraw at least {min_withdraw} $"
            )
        if amount > max_withdraw:
            raise forms.ValidationError(
                f"You Can Withdraw At Most {max_withdraw}"
            )
        if amount > balance: 
            raise forms.ValidationError(
                f"You Have {balance} $ In Your Account. "
                'You Can\'t Withdraw More Then Your Account Balance '
            )
        return amount
    
class LoanRequestForm(TransactionForms):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount') ## form e amount field e je value ta input dibe a catch korlam amount variable e
        
        return amount
    
    

class TransferForm(forms.Form):
    account_number = forms.IntegerField(
        label="Receiver Account Number"  ## field er vitore gray out kora je text thake
    )

    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2
    )