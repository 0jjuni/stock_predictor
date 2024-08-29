from .forms import CustomUserCreationForm
from django.contrib.auth.views import LogoutView
from django.views import generic
from django.urls import reverse_lazy
from predictions.models import Predict_5, minusPredict
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # 메시지 프레임워크를 사용하여 사용자에게 알림
from .forms import InterestStockForm
from .models import InterestStock
from base.models import Stock


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







@login_required
def add_interest_stock(request):
    all_stocks = Stock.objects.all()  # 전체 주식 리스트를 가져옴
    if request.method == 'POST':
        form = InterestStockForm(request.POST)
        if form.is_valid():
            stock_name = form.cleaned_data['stock_name']

            # 주식 이름이 데이터베이스에 있는지 확인
            try:
                stock = Stock.objects.get(name=stock_name)
            except Stock.DoesNotExist:
                messages.error(request, f"{stock_name} is not a valid stock name.")
                return render(request, 'accounts/add_stock.html', {'form': form, 'all_stocks': all_stocks})

            # 동일한 주식이 이미 관심 목록에 있는지 확인
            if InterestStock.objects.filter(user=request.user, stock_code=stock.code).exists():
                messages.error(request, f"{stock_name} is already in your interest list.")
            else:
                interest_stock = InterestStock(
                    user=request.user,
                    stock_name=stock.name,
                    stock_code=stock.code
                )
                interest_stock.save()
                messages.success(request, f"{stock_name} has been added to your interest list.")
                return redirect('add_interest_stock')
    else:
        form = InterestStockForm()

    return render(request, 'accounts/add_stock.html', {'form': form, 'all_stocks': all_stocks})





@login_required
def view_interest_stocks(request):
    # 사용자의 관심 주식 목록을 가져옴
    stocks = InterestStock.objects.filter(user=request.user)

    # 각 주식에 대해 예측 정보 추가
    stock_data = []
    today = timezone.now().date()

    for stock in stocks:
        predict_5_data = Predict_5.objects.filter(stock_name=stock.stock_name, created_at=today).first()
        minus_predict_data = minusPredict.objects.filter(stock_name=stock.stock_name, created_at=today).first()

        stock_data.append({
            'stock': stock,
            'predict_5_data': predict_5_data,
            'minus_predict_data': minus_predict_data
        })

    return render(request, 'accounts/view_stocks.html', {'stock_data': stock_data})