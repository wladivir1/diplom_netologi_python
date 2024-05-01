from rest_framework import serializers
from djoser.serializers import UserSerializer
from versatileimagefield.serializers import VersatileImageFieldSerializer 

from accounts.models import User, Contact
        
        

class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model.

    Hides user field and sets it to the currently authenticated user.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ('id', 'user', 'index', 'city', 'street', 'house', 'structure', 'building', 'apartment')
        read_only_fields = ('id',)

    def create(self, validated_data):
        """
        Creates and returns a Contact object with the given validated data.
        """
        contact = Contact.objects.create(**validated_data)

        return contact


class CustomUserSerializer(UserSerializer):
    """
    Custom user serializer for returning user information.

    Returns only fields that are publicly available.
    """
    
    class Meta:
        model = User
        fields = (
                'id', 
                'first_name', 
                'last_name',
                'surname', 
                'company', 
                'position', 
                'phone',
                'avatar'
                )
        read_only_fields = ('id',)


class TypeUserSerializer(serializers.ModelSerializer):
    """
    Serialize user type (client or supplier).
    """
    
    class Meta:
        model = User
        fields = ('id','type',)
        read_only_fields = ('id',)
        
class AvatarSerializer(serializers.ModelSerializer):
    """
    Serializer for user avatar image.

    Returns a serialized VersatileImageField.
    """

    avatar = VersatileImageFieldSerializer(
            sizes='user_avatar',
    )

    class Meta:
        model = User
        fields = ('id','avatar',)
        read_only_fields = ('id',)
