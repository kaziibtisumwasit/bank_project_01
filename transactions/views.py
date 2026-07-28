from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from accounts.models import UserBankAccount
from django.http import HttpResponse
from django.views.generic import CreateView,ListView,View,FormView ## Eyery Transcation need to create from -? create View
from django.contrib.auth.mixins import LoginRequiredMixin ## Like LoginRequired decoretor
from .models import Transaction
from .forms import DepositForm,TransactionForms,LoanRequestForm,WithdrawForm,TransferForm
from .constance import DEPOSIT,WITHDEAWAL,LOAN,LOAN_PAID,MONEY_SEND,MONEY_RECEIVED
from datetime import datetime
from django.db.models import Sum
# Create your views here. Classbased View te -->> Template , Model ,Form , Success_url, Context_data theke  
## Deposit + Withdraw + Take Loan


## For email 
from django.conf import settings
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string ## String theke template render korar jonno oi HTML template ta email e send korbo

  
def transaction_email(user,email_subject,amount,balance,template_name):
    message = render_to_string(template_name,{
        'user' : user, ## current user
        'amount' : amount,
        'balance' : balance,
    })## Html template ke string akare render korlam , dictionary te user,amount,balance er value ta pathalam
    to_email = user.email
    send_email = EmailMultiAlternatives(email_subject,'',to=[to_email])
    send_email.attach_alternative(message,'text/html')
    send_email.send()
  
  
## everytime every tarnscation create new form or record thats why use CreateView
## Ei view ke inherite kore withdraw,deposit,loan request korbo
## Create view data input dewar jonno form render kore ,form e dewa data validate kore, form er data save kore database e insert kore
## CreateView -->> Disply form for creating object  , it's use for create new object
##Mixin mane multiple kaj kora
## LoginRequiredMixin use korar karon holo jokhon user login na thakbe tokhon ei view e access korte parbe na

class TransactionCreateMixin(LoginRequiredMixin,CreateView): ## Ei class ta ke inherite kore onno class ghula create korbo ete code kom hobe
    template_name = 'transactions/transaction_form.html' ## Deposit,Withdraw,Loan Request er jonno same template use korbo
    model = Transaction
    title = 'Transaction' ## page er title ba heading ba page tar bar e je nam dibo ota,It's just a variabble not builtin
    success_url = reverse_lazy('transaction_report')
    ## buildin bhabe class view value pathai de kwargs ba keyword akare 
    ## jokhon kono object create hoy tokhon kono kaj korte chaile get_form_kwargs use hoi
    ##TranssactionForm er kono object create hobe ba user jokhon ei form e kono value pass korbe
    ## account value ta form er moddhe chole ashbe form er jekhane pop hocchilo
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account, ## current_user er account value ta form er moddhe pass korlam
        })   
        return kwargs
     
    def get_context_data(self, **kwargs):
        context  = super().get_context_data(**kwargs)  ##super().method_name diye method ke override kora hoi
        context.update ({
            'title' : self.title ## title variable er data ta context data hisebe frontend e pathalam
        })
        return context
        
        
## get_initial -->> Return The initial data to use for forms on this view
## user form open korar shate shate form er single ba multiple field e value fillup kore ddewa holo get_initial


class DepositeMoneyView(TransactionCreateMixin): ## TransactionCreateMixin ke inherit kore DepositMoneyView create korlam
    form_class = DepositForm
    title = "Deposit" ## TransactionCreateMixin er title variable ke override kore Deposit set korlam
    
    def get_initial(self):## Initial kono data ba specific kono data form er specific field er moddhe set kore dewa
        initial = {'transaction_type' : DEPOSIT} ## DipositForm er transaction_type field er moddhe DEPOSIT ke set kore dilam
        return initial##jokhon deposit form open korbe user tkhon transaction_type er field er moddhe DEPOSIT ta boshe jabe initially.
    
    ##request.method == 'POST' Hole form validation kortam
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount') ## DepsiteForm amount field e user je amount ta input dicche
        account = self.request.user.account ##je user ta login ache tar account model field ke catch korlam
        account.balance += amount ##Current Loggedin use er UserAccount model theke balance field  ## ex : User er old balance 500 , now 1000 taka amount deposit koealm 500+100
        account.save(  ## account model er moddhe sudhu balance fields ta update korchi
            update_fields = ['balance'] ## update_fields er moddhe list akare je field pass korbo oi field er vlaue update hoye jabe
        )
        ## Save Hower por msg show korbe
        messages.success(self.request,f"{amount} $ was deposited to your account successfully ! ")
        

        # ## Send Deposit Confirmation Email to User
        # mail_subject = "Deposit Confirmation"
        # message = render_to_string('transactions/deposit_confirmation_email.html', {
        #     'user': self.request.user,
        #     'amount': amount,
        #     'balance': account.balance,
        # }) 
        # to_email = self.request.user.email ## current user er email ta niye ashlam
        # send_email = EmailMultiAlternatives(mail_subject, '', to=[to_email]) ## EmailMessage er moddhe subject,message,receiver email pass korlam
        # send_email.attach_alternative(message, "text/html") ## EmailMessage er moddhe html template ta attach korlam
        # send_email.send() ## email send korlam
        user = self.request.user
        email_subject = "Deposit Confarmation"
        amount = amount
        balance = account.balance
        template_name = 'transactions/deposit_confirmation_email.html'
        transaction_email(user,email_subject,amount,balance,template_name) ## transaction_email function ke call korlam , user,email_subject,amount,balance,template_name pass korlam
        return super().form_valid(form)
    
    
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = "Withdraw"
    
    def get_initial(self): ## jokhon user wtihdraw button cleack korbe url er through te withdraw form render hobe oi render er somoy initially transaction_type field e ei WITHDRAWL Value ta boshe jabe
        initial = {'transaction_type': WITHDEAWAL}
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount') ## form e user je amount ta input dise oi amount ta ke niye ashlam
        account = self.request.user.account 
        account.balance -= amount
        
        ## Transction Form e save nam er ekta method make korsi oi save method ke call korsi
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request,f"{amount} $ Withdraw Successfull !")
        
        transaction_email(self.request.user,"Withdraw Confirmation",amount,account.balance,'transactions/withdraw_confirmation_email.html')
        return super().form_valid(form)
        
        
        
class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'
    
    def get_initial(self): ## initial method er maddhome form er specific field e kono value set kore dewa
        initial = {'transaction_type': LOAN} ## form er initial field e transaction_type er moddhe LOAN value set kore dilam
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        ## Transaction model er objects filter korlam jekhane account = current user account , transaction_type = LOAN , loan_approve = True tahole ami count() korbo
        current_loan_count = Transaction.objects.filter(account=self.request.user.account,transaction_type = LOAN , loan_approve = True).count()  ##user er koto ghula loan approve hoise tar count
        
        if current_loan_count >= 3:
            return HttpResponse("You Have Crossed Your Limits") ## jodi user 3 bar loan niye fele tahole eikhan theke retun hobe msg ta diye, niche ar jabe na
        messages.success(self.request,f"Loan Request for  {amount} $ are Successfully send to admin")
        
        transaction_email(self.request.user,"Loan Request Confirmation" , amount , account.balance, 'transactions/loan_request_confirmation_email.html') ## transaction_email function ke call korlam , user,email_subject,amount,balance,template_name pass korlam
        return super().form_valid(form)
    
    
    
    
##total sob post ba data ke ek shate dekhono holo classbased view er list view
## Ek template e multiple post ba multiple data dekhaono ListView -- >> Home page e o CBV er ListView Use Korbo
## Single post ba single data ke ek template e dekhano holo classbased view er detail view -->> single post full page e dekhte use hoi
## Ek template e single data ba post dekhano holo detail view
class TransactionRepostView(LoginRequiredMixin,ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction  ## je model theke data render ba show korabo
    balance = 0 ## ekta balance variable create korlam,simple variable
    title = "Transaction Report"
    
    ## GET / POST 
    ## GET URL er through te get kori jar jonno url e perameter pass korte hoi
    def get_queryset(self):
        ## jodi user kono type filter na kore taile tar total transsaction report dekhabo
        queryset=super().get_queryset().filter(
            account = self.request.user.account ## current user er account er shate transaction model er account field ke filter korlam
        )
        
        ## String Formate e pacchi date ta
        start_date_str = self.request.GET.get('start_date') ## Frontend theke start date er value ta GET method er maddhome niye ashlam
        end_date_str = self.request.GET.get('end_date') ## FRONTEND ER end date er value ta GET method er maddhome niye ashlam
        
        
        ## striptime -->> Convert date or time string  formate to date or time object
        if start_date_str and end_date_str: ## start & end date 2 tai jodi thake ba None na hoi
            start_date = datetime.strptime(start_date_str,"%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str ,"%Y-%m-%d").date()  ## object theke date 
            
            
            # queryset = queryset.filter(time_stamp_date__gte = start_date, time_stamp_date__lte = end_date) ## time stamp is a date if it's gte => greater then equal,,lte ==> lessthen equal
            ## Example : Start_date = 2023-01-01 , End_date = 2022-12-31 , then all transaction between this date will show
            queryset = queryset.filter(time_stamp__date__gte=start_date,
                                       time_stamp__date__lte=end_date)
            ## model er upor multiple function use kora hoi tokhon ei aggregate use hoi
            ##SQL Distinct ==> Return Distinct value that means database theke duplicate value raemove kore unique value ke niye ashbe
            ## current_user account or object ke get kore niye ashbo Transaction model theke, er shate filter korbo jekhane timestamp__date__gte = start_date , timestamp__date__lte = end_date
            self.balance = Transaction.objects.filter(
                time_stamp__date__gte = start_date , 
                time_stamp__date__lte = end_date
                ).aggregate(Sum('amount'))
            ['amount__sum'] ## start date theke end date er moddhe je amount thakbe er total sum hobe seta return korbe
            ## multiple type function use korar jonno aggregate function use hoi , aggregate function er moddhe Sum function use korlam jeta amount field er total sum return korbe
        else : ## jodi kono type er filter na korore ,tahole current user er banace ta dekhabe
            self.balance = self.request.user.account.balance
            ## unique queryset nibo
        return queryset.distinct()
            
    
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'account' : self.request.user.account,
            'title' : self.title,
        })
        
        return context
    
    
class PayLoanView(LoginRequiredMixin,View): ## We can use here View or CreateView , but we use View because we don't need to create any object here
    def get(self,request,loan_id):
        loan = get_object_or_404(Transaction,id=loan_id)  ## jodi ei loan_id er object pai get korbo , na pele 404 error show korbe
        if loan.loan_approve: ## Ekjon user loan pay korte parbe tokhon ei jokhon tar loan approve thakbe
            user_account = loan.account ## current user ke id diye loan variable e store kora hoise,so, ekhon user.account == loan.account
            if loan.amount < user_account.balance :## main balance theke loan amount choto hole loan pay korte parbe
                user_account.balance -= loan.amount ## Main balance theke loan mount ta minus
                loan.balance_after_transaction = user_account.balance ## loan pay korar por user er account e koto taka thakbe seta store korbe ## Like bkash e jokhon send mony kori send mony korar aghe joto taka send korbo ta main banalce theke minus kore dekhai , sheita holo balance_after_transaction
                user_account.save() 
                loan.transaction_type = LOAN_PAID ## model er transaction_type field er value ke LOAN_PAID set korlam
                # loan.time_stamp = datetime.now() ## loan pay korar somoy current date time set
                loan.save()
                
                transaction_email(user=loan.account.user,email_subject = 'Loan Paid Confirmation' , amount=loan.amount,balance=loan.balance_after_transaction,template_name='transactions/loan_paid_confirmation_email.html') ## transaction_email function ke call korlam , user,email_subject,amount,balance,template_name pass korlam
                messages.success(self.request,f"Loan Amount {loan.amount} $ Paid Successfully !")
                return redirect(reverse_lazy('transaction_report')) ## loan pay korar por transaction report page e redirect korbe
        
            else:
                messages.error(self.request , f"Loan Amount is Greater Than Available Balance")
                return redirect()
                
                
                
                
class LoanListView(LoginRequiredMixin,ListView):  ## je jinish list akare dekhabo oikhane ListView Use korbo
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'  ## classbased view theke automatically context data pathano hoi , jeta model er name diye frontend e access kora jai , jodi amra context_model_name diye name set kori tahole oi name diye frontend e access korte parbo
    ## Example : transaction ba objects diye access korte parbo , jodi amra context_model_name = 'loans' set kori tahole frontend e {{ loans }} diye access korte parbo
    ## loans ekta list akare frontend e habe, loans er upor loop through kore data ghula ke list theke ber korbo
    def get_queryset(self):  ## current user ke tar loan list ta dekhabo 
        user_account =self.request.user.account ## current user 
        queryset = Transaction.objects.filter(account = user_account, transaction_type = LOAN) ## Transaction model theke corrent user ke filter korlam tar moddhe transaction_type = LOAN je ghula te ache
        
        return queryset
    
    
    
    

class TransferMoneyView(LoginRequiredMixin, FormView):
    template_name = "transactions/transaction_form.html"
    form_class = TransferForm
    success_url = reverse_lazy("transaction_report")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Transfer Money"
        return context

    def form_valid(self, form):
        receiver_account_number = form.cleaned_data["account_number"]
        amount = form.cleaned_data["amount"]

        sender = self.request.user.account

        try:
            receiver = UserBankAccount.objects.get(
                account_no=receiver_account_number
            )

        except UserBankAccount.DoesNotExist:
            messages.error(
                self.request,
                "Receiver account not found."
            )
            return self.form_invalid(form)

        if sender == receiver:
            messages.error(
                self.request,
                "You can't transfer to your own account."
            )
            return self.form_invalid(form)

        if sender.balance < amount:
            messages.error(
                self.request,
                "Insufficient Balance."
            )
            return self.form_invalid(form)

        sender.balance -= amount
        receiver.balance += amount 

        sender.save(update_fields=["balance"])
        receiver.save(update_fields=["balance"])

        # Sender er transaction history save korlam
        Transaction.objects.create(
            account=sender,
            amount=amount,
            transaction_type=MONEY_SEND,
            balance_after_transaction=sender.balance,
        )

        # Receiver er transaction history save korlam
        Transaction.objects.create(
            account=receiver,
            amount=amount,
            transaction_type=MONEY_RECEIVED,
            balance_after_transaction=receiver.balance,
        )

        messages.success(
            self.request,
            f"${amount} transferred successfully."
        )
        
        return super().form_valid(form)
    
    
    
    
    


##############################################################
# Django Class Based Views (CBV) Cheat Sheet
##############################################################

# View
# ------------------------------------------------------------
# Base Class View
# Jokhon puro logic nije likhte hobe.
# GET, POST sob manually handle korbo.
#
# Example:
# Dashboard
# Custom API
# Custom Logic


# TemplateView
# ------------------------------------------------------------
# Sudhu HTML Template render korbe.
# Database theke data anar dorkar nai.
#
# Example:
# Home Page
# About Page
# Contact Page


# ListView
# ------------------------------------------------------------
# Multiple Object / Data Show korbe.
#
# Example:
# Transaction List
# Product List
# Employee List
# Loan History


# DetailView
# ------------------------------------------------------------
# Single Object Show korbe.
#
# Example:
# User Profile
# Single Blog
# Single Product


# CreateView
# ------------------------------------------------------------
# Database e New Object Create korbe.
#
# Example:
# Registration
# Add Product
# Create Employee
# Create Blog


# UpdateView
# ------------------------------------------------------------
# Existing Object Update korbe.
#
# Example:
# Edit Profile
# Update Address
# Edit Product


# DeleteView
# ------------------------------------------------------------
# Existing Object Delete korbe.
#
# Example:
# Delete Product
# Delete User
# Delete Blog


# FormView
# ------------------------------------------------------------
# Form Handle korbe.
# Nijer Business Logic Likhar Jonno Best.
#
# Model automatically save korbe na.
# form_valid() er moddhe sob logic likhte hobe.
#
# Example:
# Deposit Money
# Withdraw Money
# Transfer Money
# Loan Request
# Login Form
# OTP Verification


# RedirectView
# ------------------------------------------------------------
# Onno URL e Redirect korbe.
#
# Example:
# Old URL -> New URL
# Homepage Redirect


##############################################################
# Easy Rule
##############################################################

# Sudhu HTML Dekhabo?
# -> TemplateView

# Onek Data Dekhabo?
# -> ListView

# Ekta Data Dekhabo?
# -> DetailView

# Notun Data Create?
# -> CreateView

# Existing Data Update?
# -> UpdateView

# Data Delete?
# -> DeleteView

# Form Submit + Custom Logic?
# -> FormView

# Sob Logic Ami Nijer Moto Likbo?
# -> View
##############################################################