# Create your models here.
from django.db import models


class Portfolio(models.Model):
    user_id = models.IntegerField(null=True)
    username = models.CharField(max_length=30)
    stock_symbol = models.CharField(max_length=30)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    threshold = models.DecimalField(max_digits=10, decimal_places=5, default=0.00000)

    class Meta:
        db_table = "portfolio"  # Use the existing SQL table


class StockTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True)
    purchase_type = models.CharField(
        max_length=4, choices=[("BUY", "Buy"), ("SELL", "Sell")]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    stock_symbol = models.CharField(max_length=30)
    transaction_date = models.DateField(null=True)

    class Meta:
        db_table = "stock_transactions"  # Use the existing SQL table


class Anomaly(models.Model):
    AnomalyID = models.AutoField(primary_key=True)  
    StockSymbol = models.CharField(max_length=10)  
    AnomalyType = models.CharField(max_length=10)  
    AnomalyDate = models.DateField() 
    AlertTimestamp = models.DateTimeField(auto_now_add=True)  

    class Meta:
        db_table = "Anomaly"  # Use the existing SQL table
