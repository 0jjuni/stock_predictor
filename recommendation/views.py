import os
import joblib
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from base.models import Stock
import FinanceDataReader as fdr

# 프로젝트의 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 경로를 설정합니다.
model_path = os.path.join(BASE_DIR, 'models', '1day5per.pkl')

# 모델 로드 (첫 요청 시 한 번만 로드)
model = joblib.load(model_path)

def recommend_stocks(request):
    recommended_stocks = []

    # 데이터베이스에서 모든 주식 리스트를 가져옴
    stocks = Stock.objects.all()

    for stock in stocks:
        stock_code = stock.code
        stock_name = stock.name

        # 해당 주식의 데이터를 가져옴
        stock_data = fdr.DataReader(stock_code)

        if stock_data.empty:
            continue  # 데이터가 없으면 다음 주식으로 넘어감

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
            continue  # Scaler 파일이 없으면 다음 주식으로 넘어감

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
            continue  # 예측 중 오류가 발생하면 다음 주식으로 넘어감

        # 확률이 0.93 이상인 경우만 추천 리스트에 추가
        if proba >= 0.93:
            recommended_stocks.append(stock_name)

    # 추천 주식 리스트를 템플릿에 전달하여 렌더링
    context = {
        'recommended_stocks': recommended_stocks,
    }
    return render(request, 'recommendation/recommendation_list.html', context)
