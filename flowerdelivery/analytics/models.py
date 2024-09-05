from django.db import models
from flower_orders.models import Order

class Report(models.Model):
    report_date = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sales_data = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)

