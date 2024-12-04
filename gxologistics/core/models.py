from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)

class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class Metric(models.Model):
    name = models.CharField(max_length=255)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Record(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='records')
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='records')
    value = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.metric.name} - {self.value}"
