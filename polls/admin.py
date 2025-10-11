from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Question, Choice, AdvUser


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInLine]

admin.site.register(Question, QuestionAdmin)
admin.site.register(AdvUser)
