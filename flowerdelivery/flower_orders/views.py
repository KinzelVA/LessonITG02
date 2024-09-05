# flower_orders/views.py

from django.shortcuts import render

# Страница заказов
def order_list(request):
    return render(request, 'flower_orders/order_list.html')
