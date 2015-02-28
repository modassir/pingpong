from django.forms import widgets
from rest_framework import serializers

from referee.models import Players
from django.contrib.auth.models import User

class PlayerSerializer(serializers.ModelSerializer):
	owner = serializers.ReadOnlyField(source='owner.username')
	class Meta:
		model = Players
		fields = ('uid', 'name')