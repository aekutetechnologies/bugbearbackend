from django.db import models
from buguser.models import User

# Create your models here.


class Certificate(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="certificates", null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    valid_until = models.CharField(max_length=255)
    likes = models.ManyToManyField(User, related_name="certificate_likes", blank=True)
    certificate_create_date = models.CharField(max_length=255)

    def __str__(self):
        return self.title + " - " + self.user.email
