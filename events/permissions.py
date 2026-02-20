from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission,SAFE_METHODS
from .models import Event,UserOrder


class IsEventOrganizerOrReadOnly(BasePermission):
    message = "You have to be an event organizer"
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.organizer == request.user


class CanCreateOrUpdateImage(BasePermission):
    message = "You have to be an event organizer"
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.event.organizer == request.user

    def has_permission(self, request, view):
        event_slug = view.kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)
        if not event:
            return False
        return event.organizer == request.user

class CanCreateOrUpdateTickets(BasePermission):
    message = "You have to be an event organizer"
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.event.organizer == request.user

    def has_permission(self, request, view):
        event_slug = view.kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)
        if not event:
            return False
        return event.organizer == request.user


class UserCanPay(BasePermission):
    message = "You didn't request for this order."
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user

class CanCreateOrderItem(BasePermission):
    message = "You didn't create the order."
    def has_permission(self, request, view):
        order_id = view.kwargs.get('order_id')
        user_order = get_object_or_404(UserOrder, id=order_id)
        if not user_order:
            return False
        return user_order.user == request.user


class CanUpdateOrDeleteItems(BasePermission):
    message = "You can only modify your own order items."
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_order.user == request.user


class CanCreateEditor(BasePermission):
    message = "You have to be an event organizer"
    def has_permission(self, request, view):
        event_slug = view.kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)
        if not event:
            return False
        return event.organizer == request.user


