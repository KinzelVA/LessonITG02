from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_date', 'order', 'sales_data', 'profit', 'expenses')
    search_fields = ('order__id', 'report_date')
    list_filter = ('report_date',)


