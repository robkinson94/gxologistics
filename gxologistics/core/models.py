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
    description = models.TextField()  # Ensure this matches the list_display field
    target = models.FloatField()  # Ensure this matches the list_display field

    def __str__(self):
        return self.name

class Record(models.Model):
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    value = models.FloatField()
    recorded_at = models.DateTimeField(null=True)  # When the data was generated
    timestamp = models.DateTimeField(auto_now_add=True, null=True)  # When the record was added

    def __str__(self):
        return f"{self.metric.name} - {self.value}"
