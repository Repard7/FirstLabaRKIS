
from datetime import datetime

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Choice, AdvUser, UserVote
from django.template import loader
from django.urls import reverse
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object

        if self.request.user.is_authenticated:
            has_voted = UserVote.objects.filter(
                user=self.request.user,
                question=question
            ).exists()
            context['has_voted'] = has_voted
        return context

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    has_voted = UserVote.objects.filter(user=request.user, question=question).exists()

    if not request.user.is_authenticated:
        return render(request, 'polls/detail.html', {
            'question' : question,
            'error_message' : 'Вы должны зарегистрироваться для голосований'
        })
    if has_voted:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Вы уже голосовали в этом опросе',
            'has_voted': True
        })
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'вы не сделали выбор',
            'has_voted' : has_voted
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        UserVote.objects.create(user = request.user, question = question)
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        avatar = request.FILES.get('avatar')

        if password1 != password2:
            return render(request, 'polls/register.html', {'error':"Пароли не совпадают"})

        if AdvUser.objects.filter(username=username).exists():
            return render(request, 'polls/register.html', {'error' : 'Пользователь с таким именем уже существует'})

        if AdvUser.objects.filter(email=email).exists():
            return render(request, 'polls/register.html', {'error' : 'Пользователь с таким email уже существует'})

        user = AdvUser.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        if avatar:
            user.avatar = avatar
            user.save()

        login(request, user)
        return redirect('polls:index')

    return render(request, 'polls/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('polls:index')
        else:
            return render(request, 'polls/login.html', {'error' : 'Неверное имя пользователя или пароль'})
    return render(request, 'polls/login.html')

def logout_view(request):
    logout(request)
    return redirect('polls:index')

@login_required
def profile_view(request):
    if request.method == "GET":
        return render(request, 'polls/profile.html')
    if request.method == "POST":
        if 'delete_account' in request.POST:
            request.user.delete()
            logout(request)
            return redirect('polls:index')
        elif 'edit_account' in request.POST:
            return redirect('polls:edit_profile')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        avatar = request.FILES.get('avatar')

        if username and username != user.username:
            if AdvUser.objects.filter(username=username).exclude(pk=user.pk).exists():
                return render(request, 'polls/edit_profile.html', {
                    'error': 'Пользователь с таким именем уже существует'
                })
            user.username = username

        if email and email != user.email:
            if AdvUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                return render(request, 'polls/edit_profile.html', {
                    'error': 'Пользователь с таким email уже существует'
                })
            user.email = email

        if avatar:
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = avatar

        user.save()
        return redirect('polls:profile')

    return render(request, 'polls/edit_profile.html')

def create_View(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_description = request.POST.get('question_description')
        question_image = request.FILES.get('question_image')
        choices = request.POST.getlist('choices')

        if Question.objects.filter(question_text=question_text).exists():
            return render(request, 'polls/register.html', {'error' : 'Пост с таким именем уже существует'})

        question = Question.objects.create(
            question_text=question_text,
            question_description=question_description,
            pub_date=datetime.now()
        )
        if question_image:
            question.question_image = question_image
            question.save()
        valid_choices = [choice.strip() for choice in choices if choice.strip()]
        for choice_text in valid_choices:
            Choice.objects.create(
                question=question,
                choice_text=choice_text,
                votes=0
            )
        return redirect('polls:index')
    return render(request, 'polls/create.html')

