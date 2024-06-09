# serializers.py
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class OrderCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['product_name', 'quantity', 'amount', 'currency','user']
        
        
class PaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['order_id']
        
