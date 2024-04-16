from rest_framework import serializers
from djoser.serializers import UserSerializer 

from accounts.models import User, Contact
        
        

       

class ContactSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Contact
        fields = ('id', 'user', 'index', 'city', 'street', 'house', 'structure', 'building', 'apartment')
        read_only_fields = ('id',)         
        
        def create(self, validated_data):
            contact = Contact.objects.create(**validated_data)
            
        
class CustomUserSerializer(UserSerializer):
    
    class Meta(UserSerializer.Meta):
        fields = (
                'id', 
                'first_name', 
                'last_name',
                'surname', 
                'company', 
                'position', 
                'phone',
                )
        read_only_fields = ('id',) 
        
class TypeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','type',)
        read_only_fields = ('id',)      
                 