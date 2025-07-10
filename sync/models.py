# sync/models.py
from django.db import models

class DataSyncRecord(models.Model):
    user_id = models.IntegerField()
    sync_time = models.DateTimeField(auto_now_add=True)
