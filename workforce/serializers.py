from rest_framework import serializers
from .models import WorkforceGroup


class WorkforceGroupSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = WorkforceGroup
        fields = '__all__'

    def get_total_cost(self, obj):
        return obj.total_cost
