from django.contrib import admin
from .models import Flower, Order, OrderItem

# Регистрация модели Flower


# Инлайн для редактирования товаров в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Определяет количество пустых полей для добавления новых товаров

# Регистрация модели Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status')
    search_fields = ('user__username', 'status')
    list_filter = ('status',)
    inlines = [OrderItemInline]  # Добавляем инлайн для OrderItem

# Регистрация модели OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'flower', 'quantity', 'price_per_item')
    search_fields = ('order__id', 'flower_name')



