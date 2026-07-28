from django.contrib import admin
from .models import Transaction

from .views import transaction_email ## transaction_email function ke import korlam , jeta email send korar jonno use hobe


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    ## Transaction list page e kon kon field show korbe
    list_display = [
        'account',
        'amount',
        'balance_after_transaction',
        'transaction_type',
        'loan_approve'
    ]


    ## Admin panel theke Transaction save korar age ei function call hoy
    def save_model(self, request, obj, form, change):

        ## Jodi loan approve hoy
        if obj.loan_approve == True:

            ## Account balance er sathe amount add korchi
            obj.account.balance += obj.amount

            ## Transaction er porer balance store korchi
            obj.balance_after_transcation = obj.account.balance

            ## Account save korchi
            obj.account.save()

        transaction_email(user=obj.account.user,email_subject = 'Loan Approved Confirmation' , amount=obj.amount,balance=obj.account.balance,template_name='transactions/loan_approved_confirmation_email.html') ## transaction_email function ke call korlam , user,email_subject,amount,balance,template_name pass korlam
        ## Default save method call korchi
        super().save_model(request, obj, form, change) ## Overriding korar karone super() use kore default save method call korchi