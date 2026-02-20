from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event,EventImages,TicketType,UserOrder,OrderItem,Tags




class UserSerializer(serializers.ModelSerializer):
    events = serializers.SlugRelatedField(slug_field = 'slug',read_only=True,many=True)

    class Meta:
        model = User
        fields = ['username','email','events']

    def validate_email(self, value):
        if value is None or len(value) == 0:
            raise serializers.ValidationError('Email cannot be empty')

        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Email already in use")
        return value


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),  # existing tags only
        many=True,
        write_only=True
    )
    tag_names = serializers.SerializerMethodField()  # read-only names
    tickets = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and start >= end:
            raise serializers.ValidationError("Start date must be before end date")
        return data

    def get_images(self, obj):
        from .serializers import EventImageSerializer
        return EventImageSerializer(obj.images.all(), many=True).data

    def get_tag_names(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_tickets(self, obj):
        from .serializers import TicketTypeSerializer
        return TicketTypeSerializer(obj.tickets.all(), many=True).data

    def get_order_count(self,obj):
        order_count = UserOrder.objects.filter(items__ticket_type__event__slug=obj.slug).count()
        return order_count

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        event = Event.objects.create(**validated_data)
        event.tags.set(tags)
        return event

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.set(tags)
        return instance



class EventImageSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(slug_field = 'slug',read_only=True)
    class Meta:
        model = EventImages
        fields = '__all__'


# class EventEditorSerializer(serializers.ModelSerializer):
#     event = serializers.SlugRelatedField(slug_field = 'slug',read_only=True)
#     editors = serializers.ListField(write_only=True)
#     class Meta:
#         model = Event
#         fields = '__all__'
#
#     def validate(self, data):
#         event=self.context.get('event')
#         editors=data.get('editors',[])
#         for user in editors:
#             if not User.objects.filter(username=user).exists():
#                 raise serializers.ValidationError("User does not exist")
#             if event.organizer.username == user:
#                 raise serializers.ValidationError("The organizer has already editor privileges.")
#             if user in event.editors.values_list('username', flat=True):
#                 raise serializers.ValidationError(f"This user {user} is already an editor.")
#         return data
#
#     def update(self, instance, validated_data):
#         editors = validated_data.pop('editors',[])
#         for username in editors:
#             user = User.objects.get(username=username)
#             instance.editors.add(user)
#         return instance
##improved version:
class EventEditorSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    editors = serializers.ListField(write_only=True)

    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, data):
        event = self.context.get('event')
        usernames = data.get('editors', [])

        # Fetch all users that exist in one query
        users = User.objects.filter(username__in=usernames)
        found_usernames = set(users.values_list('username', flat=True))

        # Check missing users
        missing = set(usernames) - found_usernames
        if missing:
            raise serializers.ValidationError(f"Users do not exist: {', '.join(missing)}")

        # Check organizer
        if event.organizer.username in usernames:
            raise serializers.ValidationError("The organizer already has editor privileges.")

        # Check existing editors
        existing_editors = set(event.editors.values_list('username', flat=True))
        duplicates = existing_editors & set(usernames)
        if duplicates:
            raise serializers.ValidationError(f"Users already editors: {', '.join(duplicates)}")

        # Store the User objects in validated_data for use in update()
        data['editor_objs'] = list(users)
        return data

    def update(self, instance, validated_data):
        # Retrieve the pre-fetched User objects
        editor_objs = validated_data.pop('editor_objs', [])
        instance.editors.add(*editor_objs)  # Add all in one query
        return instance


class EventEditorDetailSerializer(serializers.ModelSerializer):
    editor_id = serializers.IntegerField(write_only=True, required=False)
    editor_username = serializers.CharField(source='username', read_only=True)

    class Meta:
        model = User
        fields = ['editor_id', 'editor_username']

    def validate_editor_id(self, value):
        event = self.context.get('event')
        if not event.editors.filter(id=value).exists():
            raise serializers.ValidationError("This user is not an editor of this event.")
        return value



class TicketTypeSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(slug_field = 'slug',read_only=True)
    class Meta:
        model = TicketType
        fields = '__all__'

    def validate_quantity(self, quantity):
        if quantity and quantity <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return quantity
    def validate(self, data):
        event = self.context.get('event') or getattr(self.instance, 'event', None)
        name = data.get('name') or self.instance.name
        if TicketType.objects.filter(event=event, name=name).exclude(
                pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(f"A ticket with the name '{name}' already exists for this event.")
        return data


class TagsSerializer(serializers.ModelSerializer):
    events = serializers.SlugRelatedField(slug_field = 'slug',many=True,read_only=True)
    class Meta:
        model = Tags
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    user_order = serializers.PrimaryKeyRelatedField(read_only=True)
    ticket_type = TicketTypeSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email']


class UserOrderSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = UserOrder
        fields = '__all__'


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOrder
        fields = ['status']

    def validate_status(self, value):
        order = self.instance

        if order.status != 'Pending':
            raise serializers.ValidationError(f"Order status is already {self.instance.status} and can not be changed")

        if value not in ['Paid','Cancelled']:
            raise serializers.ValidationError("Status must only be 'Paid' or 'Cancelled'")
        return value
        
    def update(self, instance, validated_data):
        new_status = validated_data['status']
        instance.status = new_status
        instance.save()
        return instance





