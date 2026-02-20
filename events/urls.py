from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import (EventViewSet,EventImageDetailedView,EventImageCreateView,
                    TicketDetailedView,TicketsCreateView,PaymentCreateView,
                    UserOrderCreateView,UserOrderListView,UserOrderRetrieveView,
                    CreateOrderItem,OrderItemListView,OrderItemDetailView
                    )

router = DefaultRouter()
router.register('events',EventViewSet,basename='events')


urlpatterns = [
    path('',include(router.urls)),
    path('events/<slug:event_slug>/images/<int:id>/',EventImageDetailedView.as_view(),name='image-detail'),
    path('events/<slug:event_slug>/images/create/',EventImageCreateView.as_view(),name='image-create'),
    path('events/<slug:event_slug>/tickets/<int:id>/',TicketDetailedView.as_view(),name='ticket-detail'),
    path('events/<slug:event_slug>/tickets/create/',TicketsCreateView.as_view(),name='ticket-create'),
    path('payment/<int:order_id>/status/',PaymentCreateView.as_view(),name='payment-create'),
    path('user/order/create/',UserOrderCreateView.as_view(),name='user-order-create'),
    path('user/orders/',UserOrderListView.as_view(),name='user-order-list'),
    path('user/order/<int:pk>/',UserOrderRetrieveView.as_view(),name='user-order-detail'),
    path('order/<int:order_id>/create/<int:ticket_id>/',CreateOrderItem.as_view(),name='order-create'),
    path('order-items/',OrderItemListView.as_view(),name='user-order-items'),
    path('order/items/<int:pk>/',OrderItemDetailView.as_view(),name='order-item-detail'),


]

