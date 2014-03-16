from django.contrib import admin

from shame.models import LineItem, Order, Product, Store, StoreOwner

admin.site.register(StoreOwner)

class StoreSpecificAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.storeowner.store == request.store

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None:
            return self._getstore(obj) == request.user.storeowner.store
        return True

    has_delete_permission = has_change_permission

    def get_queryset(self, request):
        qs = super(StoreSpecificAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(**self._query(request))

class StoreAdmin(StoreSpecificAdmin):
    def _getstore(self, obj): return obj
    def _query(self, request):
        return { 'id': request.user.storeowner.store.id }
admin.site.register(Store, StoreAdmin)

class LineItemAdmin(StoreSpecificAdmin):
    def _getstore(self, obj): return obj.order.store
    def _query(self, request):
        return { 'order__store': request.user.storeowner.store }
admin.site.register(LineItem, LineItemAdmin)

class StoreItemAdmin(StoreSpecificAdmin):
    def _getstore(self, obj): return obj.store
    def _query(self, request):
        return { 'store': request.user.storeowner.store }

class OrderAdmin(StoreItemAdmin):
    class LineItemInline(admin.TabularInline):
        model = LineItem
    inlines = [ LineItemInline ]
    search_fields = [
        'user__username', 'user__email', 'created', 'lineitem__sku']
admin.site.register(Order, OrderAdmin)

admin.site.register(Product, StoreItemAdmin)
