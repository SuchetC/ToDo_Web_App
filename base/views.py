from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm
from django import forms


from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from .forms import SignUpForm
from django.core.mail import EmailMessage


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = SignUpForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)

        email = EmailMessage(
            'Registration',
            'hello.. Welcome Todo App',
            settings.EMAIL_HOST_USER,
            [self.request.user.email],
        )
        email.fail_silently = False
        email.send()

        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    # ordering = ['title']
    #
    # paginate_by = 4
    # paginate_orphans = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):


    model = Task
    context_object_name = 'tasks'
    fields = ['title', 'description' ,'date' ,'email' ,'complete']
    widgets = {
        'date': forms.widgets.DateInput(attrs={'type': 'date'})
     }


    # queryset = Task.objects.filter(user=request.user)
    # context_object_name = 'e'
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     inpt = self.request.GET.get('email') or ''
    #     context['inpt'] = inpt


    # send_mail(
    #               'Todo Registration',
    #               'Welcome to Todo..',
    #               '2gi19mca38@students.git.edu',
    #               ['suchetc0@gmail.com'],
    #               fail_silently=False,
    #        )




    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description','date', 'complete']
    widgets = {
        'date': forms.widgets.DateInput(attrs={'type': 'date'})
    }
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))

def email(request):
    todo = Task.objects.filter(user=request.user)
    email_form = settings.EMAIL_HOST_USER
    recipient_list = request.user.email
    html_content = render_to_string('base/email.html', {'username': request.user.username, 'todo': todo, })
    c_text = strip_tags(html_content)
    send1 = EmailMultiAlternatives(
        "TodoList",
        c_text,
        email_form,
        [recipient_list, ],
    )
    send1.attach_alternative(html_content, 'text/html')
    send1.send()
    return redirect('/')


