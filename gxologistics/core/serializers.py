from rest_framework import serializers

from .models import CustomUser, Metric, Record, Team


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "is_admin"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = "__all__"


class RecordSerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source="metric.name", read_only=True)
    metric_target = serializers.FloatField(source="metric.target", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Record
        fields = "__all__"
