from django.urls import path

from .views import GetCustomerBalanceAPIView, IncreaseCustomerBalanceAPIView, DecreaseCustomerBalanceAPIView

app_name = 'account'
urlpatterns = [
    path('get/<int:customer>/<int:service>/', GetCustomerBalanceAPIView.as_view(), name='balance_get'),
    path('increase/<int:customer>/<int:service>/', IncreaseCustomerBalanceAPIView.as_view(), name='balance_increase'),
    path('decrease/<int:customer>/<int:service>/', DecreaseCustomerBalanceAPIView.as_view(), name='balance_decrease'),
]
