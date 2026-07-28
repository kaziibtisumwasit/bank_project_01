from django import forms
from django.contrib.auth.forms import UserCreationForm
from .constants import GENDER_TYPE,ACCOUNT_TYPE
from django.contrib.auth.models import User

from .models import UserAddress,UserBankAccount
## single model class filup korte forms.Modelform use kora hoi
## User jokhon multiple model class er data ekti form e fillup korbe tokhon UserCreationForm use korbe
## its create new user also add other model data under a one form

class UserRegistrationForm(UserCreationForm):
    ## UserAdderss & UserBankAccount er model er form create korlam
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'})) ## widget=forms.DateInput import date from calender
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender =forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city  = forms.CharField(max_length=50)
    postal_code =forms.IntegerField()
    country = forms.CharField(max_length=50)
    
    class Meta: ## class Meta Class er extra craracteristics add kore
        model = User ## User model er fields gular data niye form create korlam
        fields = ['username','first_name','last_name','email','account_type','birth_date','gender','street_address','city','postal_code','country','password1','password2']
        ## User Model theke username,first_name,last_name,email field gular data niye form create korlam Shate baki field ghula o nilam
    
    ### model er data ekta form er maddhome niye oi 3 ta model e ekshate fillup korechi
    ##user form fillup kortese ekta data jacche multiple model ba table e 
    def save(self,commit=True):
        created_user = super().save(commit=False) #(create_user) user object create korlam but database e ekhon save korlam na
        if commit == True:
            created_user.save() ## (create_user) user object ti database e save korlam
            ## upore je form ta fill up korlam ta User model er under e save hoie
            ##ei form theke data ghula ene ei data ghula je table ba model er oi table ba model e insert korbo
            ## cleaned_data -->> validate , clean & safe data return kore
            birth_date = self.cleaned_data.get('birth_date') ##  Form theke data ghula nicchi
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            
            ## UserAddress model e object ba row create korlam ei user er jonno
            UserAddress.objects.create(
                user = created_user,
                street_address=street_address,
                postal_code = postal_code,
                city= city,
                country= country,
            )
            
            UserBankAccount.objects.create(
                user = created_user,
                account_type = account_type,
                birth_date = birth_date,
                gender = gender,
                account_no = 100000+created_user.id,
                ##by deafult 100000 shate je user ta form fillup kortese oi user er id add kore dicchi
            )
        return created_user
    
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    'class' :(
                        'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                    )
                    
                })
            
## Je sob fields user update korte parbe oi sob fields gular jonno form create korlam
class UserUpdateForm(forms.ModelForm): ## User er data ghula update kortesi tai model form use kortesi
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender =forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city  = forms.CharField(max_length=50)
    postal_code =forms.IntegerField()
    country = forms.CharField(max_length=50)
    class Meta:
        model = User
        fields = ['first_name','last_name','email']
        
        
    def __init__(self,*args,**kwargs):  ## __init__ is a constructor method that is called when an instance of the class is created. It initializes the form and allows you to customize its behavior.
        super().__init__(*args,**kwargs)  ## Django er Built in form er __init__ method ke call korlam , overriding korar jonno super() use korlam
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                     'class' :(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                    )
                }
            )
        # if user account in database , that's called instance 
        if self.instance:
            try:
                user_account = self.instance.account ## user ba instance er account data niye aslam jodi thake tahole user_account e store korlam
                user_address = self.instance.address ## user ba instance er address data niye aslam jodi thake tahole user_address e store korlam
            except:
                user_account = None  ## jodi user_account na thake tahole user_account e None store korlam
                user_address = None  ## jodi user_address na thake tahole user_address e None store korlam
            
        if user_account:
            ## initial mane by default je value ti rakhbo form e 
            self.fields['account_type'].initial = user_account.account_type   ## initial mane by default je value ti rakhbo form e sheta user_account er account_type hobe
            self.fields['gender'].initial =user_account.gender
            self.fields['birth_date'].initial = user_account.birth_date
        if user_address:
            self.fields['street_address'].initial = user_address.street_address
            self.fields['city'].initial = user_address.city
            self.fields['postal_code'].initial = user_address.postal_code
            self.fields['country'].initial = user_address.country
                
    def save(self,commit=True):
            user = super().save(commit=False) # user model er data user variable e store korlam but database e ekhon save korlam na
            if commit:
                user.save() ## User model er data ghula database e save korlam
                
                #user jodi thake tahole user er data get kore anbo..na thakle user create korbo
                # jodi account thake tahole sheta jabe user_account
                # Jodi account na thake ta jabe created e
                user_account , created =UserBankAccount.objects.get_or_create(user=user)
                user_address , created = UserAddress.objects.get_or_create(user=user)
                ## upore je form ta fill up korlam ta User model er under e save hoie
                ##ei form theke data ghula ene ei data ghula je table ba model er oi table ba model e insert korbo
                user_account.account_type = self.cleaned_data['account_type']
                user_account.gender = self.cleaned_data['gender']
                user_account.birth_date = self.cleaned_data['birth_date']
                user_account.save()
            
                user_address.street_address = self.cleaned_data['street_address']
                user_address.city = self.cleaned_data['city']
                user_address.postal_code = self.cleaned_data['postal_code']
                user_address.country = self.cleaned_data['country']
                user_address.save()
            return user