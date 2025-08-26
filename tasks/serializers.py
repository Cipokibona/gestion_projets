from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by']

    def validate_assigned_to(self, value):
        if value and getattr(value, 'role', None) != 'manager':
            raise serializers.ValidationError("La tâche ne peut être assignée qu'à un utilisateur manager.")
        return value

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
