from django.urls import path
from .views import SignupView,LoginView,LogoutView,OtpRequestView,OtpResetView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('request/reset/', OtpRequestView.as_view(), name='request_reset'),
    path('pass/reset/', OtpResetView.as_view(), name='request_pass'),
]
