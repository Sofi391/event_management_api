from django.test import TestCase
from django.contrib.auth.models import User
from events.models import Tags,Event,EventImages,TicketType,UserOrder,OrderItem
from django.utils import timezone

class TagModelTest(TestCase):

    def test_slug_is_created(self):
        tag = Tags.objects.create(name="Rock Music")
        self.assertIsNotNone(tag.slug)
        self.assertEqual(tag.slug, "rock-music")


class EventModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="john", password="123456")

    def test_event_slug_created(self):
        event = Event.objects.create(
            title="Summer Festival",
            category="Music",
            location="Addis",
            start_date=timezone.now(),
            end_date=timezone.now(),
            organizer=self.user
        )

        self.assertEqual(event.slug, "summer-festival")


class EventImagesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="john", password="123456")
        self.event = Event.objects.create(
            title="Show",
            category="Music",
            location="Addis",
            start_date=timezone.now(),
            end_date=timezone.now(),
            organizer=self.user
        )

    def test_primary_image_auto_set(self):
        img1 = EventImages.objects.create(event=self.event, image="img1.jpg")

        self.assertTrue(img1.is_primary)

        img2 = EventImages.objects.create(event=self.event, image="img2.jpg", is_primary=True)
        img1.refresh_from_db()

        self.assertFalse(img1.is_primary)
        self.assertTrue(img2.is_primary)


class TicketTypeTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="sam")
        self.event = Event.objects.create(
            title="Expo",
            category="Tech",
            location="Addis",
            start_date=timezone.now(),
            end_date=timezone.now(),
            organizer=self.user
        )

    def test_remaining_stock_default(self):
        t = TicketType.objects.create(
            name="VIP",
            price=100,
            quantity=50,
            event=self.event
        )
        self.assertEqual(t.remaining_stock, 50)


class OrderItemTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="mike")
        self.order = UserOrder.objects.create(user=self.user)
        self.event = Event.objects.create(
            title="Concert",
            category="Music",
            location="Addis",
            start_date=timezone.now(),
            end_date=timezone.now(),
            organizer=self.user
        )
        self.ticket = TicketType.objects.create(
            name="Regular",
            price=200,
            quantity=10,
            event=self.event
        )

    def test_order_item_logic(self):
        item = OrderItem.objects.create(
            user_order=self.order,
            ticket_type=self.ticket,
            quantity=2
        )

        # Subtotal correct
        self.assertEqual(item.subtotal, 400)

        # Stock reduced
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.remaining_stock, 8)

        # Order total correct
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, 400)


class UserOrderTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="mike")

    def test_paid_sets_date(self):
        order = UserOrder.objects.create(user=self.user)

        self.assertIsNone(order.paid_at)

        order.status = "Paid"
        order.save()

        self.assertIsNotNone(order.paid_at)
