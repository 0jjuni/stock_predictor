from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm  # 새로운 폼 임포트
from django.contrib.auth.views import LogoutView
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # 회원가입 후 로그인 페이지로 이동
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        form.save()  # 사용자 저장
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        # GET 요청을 POST 요청처럼 처리하여 로그아웃을 실행합니다.
        return self.post(request, *args, **kwargs)
