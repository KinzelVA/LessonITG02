# analytics/admin.py
from django.contrib import admin
from .models import Report
from django.utils.timezone import now


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_date', 'order', 'sales_data', 'profit', 'expenses')
    search_fields = ('order__id', 'report_date')
    list_filter = ('report_date',)


    # Действие для создания отчетов вручную
    actions = ['create_manual_report']

    def create_manual_report(self, request, queryset):
        # Создание отчета для выбранных заказов
        for order in queryset:
            # Пример создания отчета
            Report.objects.create(
                report_date=now().date(),
                order=order,
                sales_data=order.total_price,  # Используем данные заказа для отчета
                profit=order.total_price,  # Можно модифицировать под нужды
                expenses=0  # Если есть данные по расходам
            )
        self.message_user(request, "Отчеты успешно созданы для выбранных заказов.")

    create_manual_report.short_description = "Создать отчет для выбранных заказов"


