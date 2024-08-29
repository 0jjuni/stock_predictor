import os
import joblib
import pandas as pd
from django.shortcuts import render
from django.utils import timezone
from .models import Recommendation
from predictions.models import minusPredict
from base.models import Stock
import FinanceDataReader as fdr
from django.utils.timezone import localdate, now

# 프로젝트의 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 경로를 설정합니다.
model_path = os.path.join(BASE_DIR, 'models', '1day5per.pkl')

# 모델 로드 (첫 요청 시 한 번만 로드)
model = joblib.load(model_path)

def recommend_stocks(request=None):
    today = localdate()  # 로컬 시간대의 현재 날짜를 가져옴

    # 비교하는 오늘 날짜 출력
    print(f"Today (Comparison Date): {today}")

    # 오늘 날짜로 추천 데이터 필터링
    recommendations = Recommendation.objects.filter(created_at=today)

    # 각 Recommendation 객체의 created_at 날짜 출력
    for rec in recommendations:
        print(f"Stock Name: {rec.stock_name}, Created At: {rec.created_at}")

    if recommendations.exists():
        print("Existing recommendations found for today.")
        recommended_stocks_list = [{'name': rec.stock_name, 'code': rec.stock_code} for rec in recommendations]
    else:
        print("No recommendations found for today, generating new recommendations.")
        recommended_stocks_list = []

        # 오늘 이전의 추천 데이터 및 관련 minusPredict 데이터를 삭제
        Recommendation.objects.filter(created_at__lt=today).delete()
        minusPredict.objects.filter(created_at__lt=today).delete()

        # 모든 주식 리스트 가져옴
        stocks = Stock.objects.all()

        for stock in stocks:
            stock_code = stock.code
            stock_name = stock.name

            # 주식 데이터를 가져옴
            stock_data = fdr.DataReader(stock_code)

            if stock_data.empty:
                continue

            last_row = stock_data.iloc[-1]
            open_price = last_row['Open']
            high = last_row['High']
            low = last_row['Low']
            close = last_row['Close']
            volume = last_row['Volume']

            scaler_path = os.path.join(BASE_DIR, 'scaler', f'{stock_name}_scaler.pkl')

            if not os.path.exists(scaler_path):
                continue

            scaler = joblib.load(scaler_path)

            input_data = pd.DataFrame([[close, volume, open_price, high, low]],
                                      columns=['Close', 'Volume', 'Open', 'High', 'Low'])

            scaled_data = scaler.transform(input_data)

            try:
                proba = model.predict_proba(scaled_data)[0][1]
            except Exception as e:
                continue

            prediction = 1 if proba >= 0.96 else 0

            if prediction == 1:
                # 중복 확인 후 추가
                if not Recommendation.objects.filter(stock_name=stock_name, created_at=today).exists():
                    Recommendation.objects.create(stock_name=stock_name, stock_code=stock_code, created_at=today)
                    recommended_stocks_list.append({'name': stock_name, 'code': stock_code})

            # 예측 결과를 minusPredict 모델에 저장 (1 또는 0)
            minusPredict.objects.create(stock_name=stock_name, stock_code=stock_code, prediction=prediction, created_at=today)

    if request:
        context = {
            'recommended_stocks': recommended_stocks_list,
        }
        return render(request, 'recommendation/recommendation_list.html', context)
    else:
        return recommended_stocks_list
