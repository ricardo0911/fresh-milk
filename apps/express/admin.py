from django.contrib import admin
from .models import ExpressCompany, ExpressOrder, ExpressTrace


@admin.register(ExpressCompany)
class ExpressCompanyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'is_default', 'created_at']
    list_filter = ['is_active', 'is_default']
    search_fields = ['code', 'name']


@admin.register(ExpressOrder)
class ExpressOrderAdmin(admin.ModelAdmin):
    list_display = ['express_no', 'express_company', 'order', 'status', 'created_at']
    list_filter = ['status', 'express_company']
    search_fields = ['express_no', 'order__order_no']
    raw_id_fields = ['order']


@admin.register(ExpressTrace)
class ExpressTraceAdmin(admin.ModelAdmin):
    list_display = ['express_order', 'time', 'description', 'location']
    list_filter = ['express_order__express_company']
    search_fields = ['express_order__express_no', 'description']
