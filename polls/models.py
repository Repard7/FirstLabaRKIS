import datetime
from random import choice

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.timezone import now


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    question_description = models.TextField(blank=True)
    question_image = models.ImageField(upload_to='question_images/', blank=True, null=True, verbose_name='Изображение опроса')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def total_votes(self):
        return sum(choice.votes for choice in self.choice_set.all())

    def __str__(self):
        return self.question_text

    def is_expired(self):
        return timezone.now() > self.pub_date + datetime.timedelta(minutes=10)

    @classmethod
    def create_question(cls, question_text, question_description=""):
        return cls.objects.create(
            question_text=question_text,
            question_description=question_description
        )
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    def get_percentage(self):
        total = self.question.total_votes()
        if total == 0:
            return 0
        return (self.votes / total) * 100

class AdvUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=False, null=False, verbose_name='Аватар')
    email = models.EmailField(unique=True, verbose_name='Email адрес')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class UserVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE)