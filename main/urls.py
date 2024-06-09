# urls.py
from django.urls import path
from .views import (CreateOrderAndInitiatePaymentView,
                    PaymentCallbackView,
                    # PaymentSuccessView,
                    SaveCardView,
                    PayWithSavedCardView,
                   
)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    
    path('create-order-and-initiate-payment/', CreateOrderAndInitiatePaymentView.as_view(), name='create_order_and_initiate_payment'),
    path('payment-result/', PaymentCallbackView.as_view(), name='payment_success'),
    # path('payment-result/', PaymentSuccessView.as_view(), name='payment_success'),


    path('save-card/', SaveCardView.as_view(), name='save_card'),
    path('pay-with-saved-card/', PayWithSavedCardView.as_view(), name='pay_with_saved_card'),
    


]



{
    "user": 1,
    "product_name": "Blue Jacket",
    "quantity": 2,
    "amount": 4,
    "currency": "AZN",
    "status": "Pending"
}
