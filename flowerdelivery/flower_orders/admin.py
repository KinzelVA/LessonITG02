from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'status', 'address')
    search_fields = ('user__username', 'status')
    list_filter = ('status',)
    date_hierarchy = 'order_date'

