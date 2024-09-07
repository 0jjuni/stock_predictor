from django.shortcuts import render
from django.http import HttpResponseBadRequest
from base.models import Stock  # base 앱의 모델
from predictions.models import Predict_5, minusPredict  # predictions 앱의 모델
from django.utils import timezone
import FinanceDataReader as fdr


def home(request):
    stock_name_list = Stock.objects.values_list('name', flat=True)  # 전체 주식 목록

    if request.method == 'POST':
        stock_name = request.POST.get('stock_name', '').strip()

        try:
            stock_info = Stock.objects.get(name=stock_name)
        except Stock.DoesNotExist:
            return HttpResponseBadRequest(f"주식명 '{stock_name}'을(를) 찾을 수 없습니다.")

        today = timezone.now().date()

        # 주식 데이터를 가져옴
        stock_data = fdr.DataReader(stock_info.code)
        if stock_data.empty:
            return HttpResponseBadRequest(f"해당 주식 '{stock_name}'의 데이터를 불러올 수 없습니다.")

        # 데이터프레임의 마지막 행(가장 최근 데이터)에서 필요한 열 추출 및 날짜 추출
        last_row = stock_data.iloc[-1]
        date = last_row.name.strftime('%Y-%m-%d')  # 인덱스에서 날짜를 yyyy-mm-dd 형식으로 추출
        open_price = last_row['Open']
        high = last_row['High']
        low = last_row['Low']
        close = last_row['Close']
        volume = last_row['Volume']

        # Predict_5 모델에서 데이터를 가져옴
        predict_5_data = Predict_5.objects.filter(stock_name=stock_name, created_at=today).first()

        # minusPredict 모델에서 데이터를 가져옴
        minus_predict_data = minusPredict.objects.filter(stock_name=stock_name, created_at=today).first()

        context = {
            'stock_name': stock_name,
            'date': date,
            'open_price': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'stock_name_list': stock_name_list,
            'predict_5_data': predict_5_data,
            'minus_predict_data': minus_predict_data,
        }

        # 예측 결과는 새로운 페이지에 렌더링
        return render(request, 'predictions/prediction_result.html', context)  # base 앱의 home.html

    # GET 요청 시 홈 화면을 기본적으로 렌더링
    return render(request, 'base/home.html', {'stock_name_list': stock_name_list})


def model_performance(request):
    # 5% 상승 예측 모델 성능 지표
    predict_5_performance = {
        'accuracy': 0.96,
        'precision': 0.72,
    }

    # 5% 하락 예측 모델 성능 지표
    minus_predict_performance = {
        'accuracy': 0.96,
        'precision': 0.43,
        'recall': 0.35,
        'f1_score': 0.39,
    }

    context = {
        'predict_5_performance': predict_5_performance,
        'minus_predict_performance': minus_predict_performance,
    }

    return render(request, 'base/model_performance.html', context)
