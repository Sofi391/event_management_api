from dataclasses import fields

from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.text import slugify
import unidecode
from rest_framework.exceptions import ValidationError


# Create your models here.
class Tags(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True,blank=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode.unidecode(self.name))
            slug = base_slug
            counter = 1

            # Handle duplicate slugs
            while Tags.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


class Event(models.Model):
    title = models.CharField(max_length=100,null=False)
    description = models.TextField(null=True,blank=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=False,unique=True,blank=True)

    organizer = models.ForeignKey(User, on_delete=models.CASCADE,related_name="events")
    tags = models.ManyToManyField(Tags,related_name="events")
    editors = models.ManyToManyField(User,related_name="event_editor",blank=True)

    class Meta:
        ordering = ('-start_date',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode.unidecode(self.title))
            slug = base_slug
            counter = 1

            # Handle duplicate slugs
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


class EventImages(models.Model):
    image = models.ImageField(null=False,blank=False,upload_to='event_images',default='event_images/default.jpg')
    caption = models.TextField(null=True,blank=True)
    is_primary = models.BooleanField(default=False)

    event = models.ForeignKey(Event, on_delete=models.CASCADE,related_name="images")
    def __str__(self):
        return self.event.title

    def save(self, *args, **kwargs):
        if self.is_primary:
            EventImages.objects.filter(event=self.event, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        elif not self.event.images.filter(is_primary=True).exists():
            self.is_primary = True
        super().save(*args, **kwargs)


class TicketType(models.Model):
    name = models.CharField(max_length=100,null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(null=False)
    remaining_stock = models.PositiveIntegerField(blank=True,null=True)
    slug = models.SlugField(null=False,unique=True,blank=True)

    event = models.ForeignKey(Event, on_delete=models.CASCADE,related_name="tickets")

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['event', 'name'],name='unique_name_per_event')
        ]

    def save(self, *args, **kwargs):
        if self.remaining_stock is None:
            self.remaining_stock = self.quantity

        if not self.slug:
            base_slug = slugify(unidecode.unidecode(self.name))
            slug = base_slug
            counter = 1

            # Handle duplicate slugs
            while TicketType.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)



class UserOrder(models.Model):
    user_choice = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    status = models.CharField(choices=user_choice, max_length=20,default='Pending')
    paid_at = models.DateTimeField(blank=True,null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="orders")

    class Meta:
        ordering = ('-paid_at',)

    def __str__(self):
        return f"{self.user.username}-{self.status}"

    def save(self, *args, **kwargs):
        if self.status == 'Paid' and self.paid_at is None:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(null=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)

    user_order = models.ForeignKey(UserOrder, on_delete=models.CASCADE,related_name="items")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE,related_name="items")

    def __str__(self):
        return f"{self.user_order.user.username}-{self.ticket_type.name}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Lock the ticket type row to prevent race conditions
        ticket_type = TicketType.objects.select_for_update().get(pk=self.ticket_type.pk)
        
        if self.quantity > ticket_type.remaining_stock:
            raise ValidationError("Not enough stock")
        
        ticket_type.remaining_stock -= self.quantity
        ticket_type.save(update_fields=['remaining_stock'])

        self.subtotal = self.quantity * ticket_type.price
        super().save(*args,**kwargs)

        total = sum([item.subtotal for item in self.user_order.items.all()])
        self.user_order.total_price = total
        self.user_order.save(update_fields=['total_price'])


