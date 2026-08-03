from django.urls import path
from . import views

urlpatterns=[
    path('user_registration/',views.UserRegistrationView.as_view(),name='registration'),
    # path('logout/',views.UserLogout.as_view(),name='logout'),
    path('login/',views.UserLoginView.as_view(),name='login'),
    path('logout/',views.userLogout,name='logout'),
    path('profile/',views.UserProfileUpdate.as_view(),name='profile_update'),
    path('change_password/',views.ChangePassword.as_view(),name='change_password'),
]