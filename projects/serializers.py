from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def validate_status(self, value):
        project = self.instance
        from finance.models import Advance

        if value == "in_progress":
            has_advance = Advance.objects.filter(project=project).exists()
            if not has_advance:
                raise serializers.ValidationError(
                    "Impossible de passer le projet en 'in_progress' sans au moins une avance enregistrée."
                )
        return value
