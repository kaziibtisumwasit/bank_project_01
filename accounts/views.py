from django.shortcuts import render,redirect
from django.views.generic import FormView
from django.contrib.auth.views import LoginView,LogoutView
from .forms import UserRegistrationForm ,UserUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth import login,logout
from django.views import View
# Create your views here.
##Class based View
##For form --> formview
##For Showing Details of specific --> detailsview
##For Showing multiple elements or multiple things or showing multiple product - >> listview

##Templete_name = Je template e show korbo 
##form_class = Je form ta render korbo 
## success_url = je 
## CreateView --> Single  Model handle kore
## FormView --> Multiple Model handle kore
class UserRegistrationView(FormView):
    template_name = 'accounts/reg.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile_update')
    
    def form_valid(self,form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request,user) ## JE user ti request korse oi user ke login korlam
        print(user)
        return super().form_valid(form) # this function call it self ,If everything are correct
    
        
class UserLoginView(LoginView):
    template_name ='accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')
    
class UserLogout(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')

def userLogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')




class UserProfileUpdate(View):
    template_name = 'accounts/profile.html'
    # title = "Update Profile"

    def get(self, request): ## page visit time e user ke ja show korbe ta get
        form = UserUpdateForm(instance=request.user) ## request.user holo current logged in user, instance=request.user means the form will be pre-filled with the current user's data
        ## instace = request.user dewar karone form er field ghula current logged in user er data diye pre-filled hobe. jodi instance na dewa hoy tahole form er field gula empty thakbe.
        return render(request, self.template_name, {'form': form})

    def post(self, request):   ## user jokhon form submit korbe tokhon post method use hoi
        form = UserUpdateForm(request.POST, instance=request.user)  ## request.POST holo user er dewa notun data , instance =request.user holo current user er data.instance dewa te notun user create hobe na aghe user er data updata korbe
        if form.is_valid(): ## Form validation check korbe
            ## form ta jodi valid na hoi form e error msg show korbe
            form.save() ## jodi valid hoi database e save hobe
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form}) ## template render hobe , frontend e form pathabe
    
    # def get_context_data(self,**kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = self.title
    #     return context