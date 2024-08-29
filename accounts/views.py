from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm  # 새로운 폼 임포트
from django.contrib.auth.views import LogoutView

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        # GET 요청을 POST 요청처럼 처리하여 로그아웃을 실행합니다.
        return self.post(request, *args, **kwargs)
