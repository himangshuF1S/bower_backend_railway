from rest_framework import serializers
from .models import Session

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            "title", "description", "created_by", "created_by_mentor", 
            "event_type", "start_time", "end_time", "recurring_type"
        ]
