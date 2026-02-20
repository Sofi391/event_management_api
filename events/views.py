from rest_framework.authtoken.admin import User
from rest_framework.viewsets import ModelViewSet
from .models import Event,EventImages,TicketType,UserOrder,OrderItem,Tags
from .serializers import (EventSerializer, TagsSerializer, EventImageSerializer,
                          UserSerializer, UserOrderSerializer,
                          OrderItemSerializer, TicketTypeSerializer,PaymentStatusSerializer,
                          EventEditorSerializer,EventEditorDetailSerializer,
                          )
from rest_framework import filters, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, UpdateAPIView, \
    RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework import serializers
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny,IsAuthenticated
from .permissions import (IsEventOrganizerOrReadOnly,CanCreateOrUpdateImage,
                          CanCreateOrUpdateTickets,UserCanPay,CanCreateOrderItem,
                          CanUpdateOrDeleteItems,CanCreateEditor,
                          )



# Create your views here.
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'slug'

    filter_backends = (filters.SearchFilter,filters.OrderingFilter)
    search_fields = ('title','tags__name','category','start_date','location','organizer__username')
    ordering_fields = ('start_date','created_at','tickets__price')
    ordering = ('start_date',)

    def get_queryset(self):
        queryset = super().get_queryset()
        event_name = self.request.query_params.get('event_name')
        category = self.request.query_params.get('category')
        tags = self.request.query_params.get('tags')
        created_at = self.request.query_params.get('created_at')
        sold_status = self.request.query_params.get('state')

        if event_name:
            queryset = queryset.filter(title__icontains=event_name)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if tags:
            queryset = queryset.filter(tags__name__icontains=tags)
        if created_at:
            queryset = queryset.filter(created_at__gte=created_at)
        if sold_status:
            if sold_status == 'active':
                queryset = queryset.filter(tickets__remaining_stock__gt=0)
            elif sold_status == 'inactive':
                queryset = queryset.filter(tickets__remaining_stock=0)
        return queryset

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated,IsEventOrganizerOrReadOnly]

        return [permission() for permission in permission_classes]


    def perform_create(self, serializer):
        return serializer.save(organizer=self.request.user)


class EventImageCreateView(CreateAPIView):
    queryset = EventImages.objects.all()
    serializer_class = EventImageSerializer
    permission_classes = [IsAuthenticated,CanCreateOrUpdateImage]

    def perform_create(self, serializer):
        event = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        return serializer.save(event=event)


class EventImageDetailedView(RetrieveUpdateDestroyAPIView):
    queryset = EventImages.objects.all()
    serializer_class = EventImageSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthenticated,CanCreateOrUpdateImage]

    def get_queryset(self):
        return EventImages.objects.filter(event__slug=self.kwargs['event_slug'])


class EventEditorCreateView(UpdateAPIView):
    serializer_class = EventEditorSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated,CanCreateEditor]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['event'] = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        return context

    def perform_update(self, serializer):
        event = self.get_object()
        return serializer.update(event,serializer.validated_data)

##check this later!!
class EventEditorDetailedView(RetrieveUpdateDestroyAPIView):
    serializer_class = EventEditorDetailSerializer
    permission_classes = [IsAuthenticated, CanCreateEditor]
    lookup_url_kwarg = 'editor_id'

    def get_queryset(self):
        # Only fetch editors for the specific event
        event_slug = self.kwargs['event_slug']
        event = get_object_or_404(Event, slug=event_slug)
        return event.editors.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pass the event to the serializer for validation
        event_slug = self.kwargs['event_slug']
        event = get_object_or_404(Event, slug=event_slug)
        context['event'] = event
        return context

    def perform_destroy(self, instance):
        # Remove editor from event instead of deleting the user
        event = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        event.editors.remove(instance)


class TicketsCreateView(CreateAPIView):
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer
    permission_classes = [IsAuthenticated,CanCreateOrUpdateTickets]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['event'] = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        return context

    def perform_create(self, serializer):
        event = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        return serializer.save(event=event)


class TicketDetailedView(RetrieveUpdateDestroyAPIView):
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return TicketType.objects.filter(event__slug=self.kwargs['event_slug'])

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated,CanCreateOrUpdateTickets]
        return [permission() for permission in permission_classes]


class UserOrderCreateView(CreateAPIView):
    queryset = UserOrder.objects.all()
    serializer_class = UserOrderSerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class UserOrderListView(ListAPIView):
    serializer_class = UserOrderSerializer

    def get_queryset(self):
        queryset = UserOrder.objects.filter(user=self.request.user)

        status = self.request.query_params.get('status')
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')

        if status:
            queryset = queryset.filter(status__icontains = status)
        if from_date:
            queryset = queryset.filter(paid_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(paid_at__lte=to_date)

        return queryset


class UserOrderRetrieveView(RetrieveAPIView):
    serializer_class = UserOrderSerializer

    def get_queryset(self):
        return UserOrder.objects.filter(user=self.request.user)


class PaymentCreateView(UpdateAPIView):
    queryset = UserOrder.objects.all()
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsAuthenticated,UserCanPay]

    def get_object(self):
        return get_object_or_404(UserOrder,id=self.kwargs['order_id'],user=self.request.user)

    def perform_update(self, serializer):
        order = serializer.save()

        if order.status == "Paid":
            try:
                send_mail(
                    subject="Payment Successful",
                    message=f"Your payment of {order.total_price} ETB was successful!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.user.email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"Unable to send email, {e}")


class CreateOrderItem(CreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated,CanCreateOrderItem]

    def perform_create(self, serializer):
        user_order = get_object_or_404(UserOrder, id=self.kwargs['order_id'],user = self.request.user)
        ticket_type = get_object_or_404(TicketType, id=self.kwargs['ticket_id'])

        if user_order.items.exists() and user_order.items.first().ticket_type.event != ticket_type.event:
            raise serializers.ValidationError("The ticket is not for the same event as the other items in this order.")

        return serializer.save(user_order=user_order, ticket_type=ticket_type)


class OrderItemListView(ListAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        event_search = self.request.query_params.get('event', None)

        queryset = OrderItem.objects.filter(user_order__user=self.request.user)
        if event_search:
            queryset = queryset.filter(
                Q(ticket_type__event__title__icontains=event_search) |
                Q(ticket_type__event__slug__icontains=event_search) |
                Q(ticket_type__event__category__icontains=event_search) |
                Q(ticket_type__name__icontains=event_search)
            )

        return queryset.distinct()


class OrderItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated,CanUpdateOrDeleteItems]

    def get_queryset(self):
        return OrderItem.objects.filter(user_order__user=self.request.user)



