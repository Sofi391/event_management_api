from django.contrib import admin
from .models import Event,EventImages,TicketType,OrderItem,UserOrder,Tags

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','category','start_date','end_date')
    list_filter = ('location','created_at','start_date',)

@admin.register(EventImages)
class EventImagesAdmin(admin.ModelAdmin):
    list_display = ('event','caption','image')
    list_filter = ('event__title',)

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('event','name','price','quantity','remaining_stock')
    list_filter = ('name','price',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('user_order','ticket_type','ticket_type__event__title','quantity','subtotal')
    list_filter = ('user_order__user__username','ticket_type')

@admin.register(UserOrder)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = ('user','total_price','status','paid_at')
    list_filter = ('status','paid_at','user',)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

