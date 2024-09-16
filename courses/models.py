from django.db import models

# Create your models here.

from buguser.models import User


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Course((models.Model)):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to="courses", null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="course_likes", blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def get_total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.name


class CourseModule(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseReview(models.Model):
    course = models.ForeignKey(Course, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=200)
    rating = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s - %s" % (self.course.name, self.name, self.id)


class CourseOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.course.name, self.user.email)

    def calculate_progress(self):
        total_modules = self.course.modules.count()
        completed_modules = self.courseprogress.completed_modules.count()
        return (completed_modules / total_modules) * 100


# Added the CourseProgress model
class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_modules = models.ManyToManyField(
        CourseModule, related_name="completed_modules"
    )
    date_completed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.course.name, self.user.email)

    def calculate_progress(self):
        total_modules = self.course.modules.count()
        completed_modules = self.completed_modules.count()
        return (completed_modules / total_modules) * 100


class CourseModuleQuiz(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class UserCourseQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(CourseModuleQuiz, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    date_answered = models.DateTimeField(auto_now_add=True)
    answered_correctly = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.user.email, self.quiz.question)
