# analytics/models.py
from django.db import models
from flower_orders.models import Order

class Report(models.Model):
    report_date = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sales_data = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Отчёт от {self.report_date} по заказу {self.order.id}"

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"
