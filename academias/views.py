from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Academia
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

class AcademiaView(LoginRequiredMixin):
    login_url = 'academias_login'

    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        username = request.user.username or None
        academias = Academia.objects.filter(cnpj=username)
        if academias.exists():
            return render(request, self.template_name, *args, **kwargs)
        else:
            #desloga e redireciona para login de academia
            logout(request)
            messages.error(request, 'Academia não encontrada!')
            return redirect('academias_login')    

class LoginView(TemplateView):
    template_name = 'academias/login.html'

    def get(self, request, *args, **kwargs):
        #verificando se o usuário está logado
        if request.user.is_authenticated:
            return redirect('academias_index')
        else:
            return render(request, self.template_name, context=None)
        
    def post(self, request, *args, **kwargs):
        cnpj = request.POST.get('cnpj')
        senha = request.POST.get('senha')

        #verificando se o usuário existe
        user = authenticate(request, username=cnpj, password=senha)
        if user is not None:
            login(request, user)
            return redirect('academias_index')
        else:
            messages.error(request, 'CNPJ ou senha inválidos!')
            return redirect('academias_login')

class AcademiaDashboardView(AcademiaView, TemplateView):
    template_name = 'academias/index.html'

#criando receiver para quando academia for criada, atualizada ou deletada
@receiver(post_save, sender=Academia)
def create_user(sender, instance, created, **kwargs):
    if created:
        user = User.objects.create_user(username=instance.cnpj, password=instance.senha)
        user.save()

    else:
        user = User.objects.get(username=instance.cnpj)
        user.set_password(instance.senha)
        user.save()


@receiver(post_delete, sender=Academia)
def delete_user(sender, instance, **kwargs):
    user = User.objects.get(username=instance.email)
    user.delete()
    
