from django.db import models

class User(models.Model):
    user_agent = models.TextField()
    ip_address = models.TextField()
    n_connections = models.IntegerField()
    last_date_connected = models.DateTimeField()

    def __str__(self):
        return self.user_agent