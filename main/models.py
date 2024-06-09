# models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='AZN')
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_id = models.PositiveIntegerField(null=True,blank=True)
    session_id = models.CharField(max_length=100,null=True,blank=True)


