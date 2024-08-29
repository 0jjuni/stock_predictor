from django.shortcuts import render
from django.http import HttpResponseBadRequest
from base.models import Stock  # 'base'는 앱 이름입니다. 실제 사용 중인 앱 이름으로 변경하세요.
import FinanceDataReader as fdr
import os
import joblib
import pandas as pd

# 프로젝트의 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 경로를 설정합니다.
model_path = os.path.join(BASE_DIR, 'models', '1day5per.pkl')

# 모델 로드 (첫 요청 시 한 번만 로드)
model = joblib.load(model_path)

def predict_stock(request):
    # 데이터베이스에서 주식 리스트를 가져옴
    stock_name_list = Stock.objects.values_list('name', flat=True)

    if request.method == 'POST':
        stock_name = request.POST.get('stock_name', '').strip()

        # 데이터베이스에서 주식명에 해당하는 코드를 조회
        try:
            stock_info = Stock.objects.get(name=stock_name)
        except Stock.DoesNotExist:
            return HttpResponseBadRequest(f"주식명 '{stock_name}'을(를) 찾을 수 없습니다.")

        stock_code = stock_info.code

        # 해당 주식의 데이터를 가져옴
        stock_data = fdr.DataReader(stock_code)

        if stock_data.empty:
            return HttpResponseBadRequest(f"해당 주식 '{stock_name}'의 데이터를 불러올 수 없습니다.")

        # 데이터프레임의 마지막 행(가장 최근 데이터)에서 필요한 열 추출
        last_row = stock_data.iloc[-1]
        open_price = last_row['Open']
        high = last_row['High']
        low = last_row['Low']
        close = last_row['Close']
        volume = last_row['Volume']

        # Scaler 파일 경로 설정 및 로드
        scaler_path = os.path.join(BASE_DIR, 'scaler', f'{stock_name}_scaler.pkl')

        if not os.path.exists(scaler_path):
            return HttpResponseBadRequest(f"해당 주식 '{stock_name}'에 대한 스케일러를 찾을 수 없습니다.")

        scaler = joblib.load(scaler_path)

        # 입력 데이터를 DataFrame으로 변환하여 피처 이름을 제공
        input_data = pd.DataFrame([[close, volume, open_price, high, low]],
                                  columns=['Close', 'Volume', 'Open', 'High', 'Low'])

        # 스케일링
        scaled_data = scaler.transform(input_data)

        # 예측 확률 수행
        try:
            proba = model.predict_proba(scaled_data)[0][1]  # 클래스 1의 확률
        except Exception as e:
            return HttpResponseBadRequest(f"예측 중 오류가 발생했습니다: {str(e)}")

        # 확률이 0.96 이상인 경우에만 1로 설정
        prediction = 1 if proba >= 0.96 else 0

        # 예측 결과와 추가 정보를 템플릿에 전달하여 렌더링
        context = {
            'stock_name': stock_name,
            'open_price': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'prediction': prediction,
            'stock_name_list': stock_name_list,  # 주식명 리스트를 템플릿에 전달
        }
        return render(request, 'predictions/prediction_result.html', context)

    return render(request, 'predictions/predict.html', {'stock_name_list': stock_name_list})
