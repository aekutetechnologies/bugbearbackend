from django.db import models
from buguser.models import User

# Create your models here.


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="posts", null=True)
    likes = models.ManyToManyField(User, related_name="post_likes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_likes(self):
        return self.likes.count()

    def get_total_comments(self):
        return len(self.comments_json)

    def __str__(self):
        return self.title


""" Comment model """


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="blogcomment", blank=True)
    reply = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.CASCADE
    )

    def total_clikes(self):
        return self.likes.count()

    def __str__(self):
        return "%s - %s - %s" % (self.post.title, self.name, self.id)


class PostCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
