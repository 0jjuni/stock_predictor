from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label=_("사용자 이름"),
        help_text=_("150자 이하의 문자, 숫자, 그리고 @/./+/-/_ 만 가능합니다."),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label=_("비밀번호"),
        help_text=_("비밀번호는 8자 이상이어야 하며, 개인 정보와 유사하지 않아야 합니다."),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_("비밀번호 확인"),
        help_text=_("위와 동일한 비밀번호를 입력하세요."),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
