import os
import joblib
import pandas as pd
import FinanceDataReader as fdr
from django.utils.timezone import localdate, now
from base.models import Stock
from predictions.models import minusPredict
from datetime import time

# 프로젝트의 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 경로를 설정합니다.
model_path = os.path.join(BASE_DIR, 'models', 'minus5per.pkl')

# 모델 로드 (첫 요청 시 한 번만 로드)
model = joblib.load(model_path)

def predict_and_save_stocks():
    today = localdate()
    now_time = now().time()
    is_after_market_close_now = now_time >= time(15, 30)

    stocks = Stock.objects.all()

    # 오늘 날짜의 예측 결과 삭제가 아닌, 어제 데이터가 있는 경우 업데이트를 위한 처리를 합니다.
    for stock in stocks:
        stock_name = stock.name
        stock_code = stock.code

        stock_data = fdr.DataReader(stock_code)
        if stock_data.empty:
            print(f"해당 주식 '{stock_name}'의 데이터를 불러올 수 없습니다.")
            continue

        # 파생변수 추가
        stock_data['MA_5'] = stock_data['Close'].rolling(window=5).mean()
        stock_data['Volume_MA_10'] = stock_data['Volume'].rolling(window=10).mean()
        stock_data['Volatility'] = stock_data['Close'].rolling(window=10).std()
        stock_data['EMA_12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
        stock_data['EMA_26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()
        stock_data['MACD'] = stock_data['EMA_12'] - stock_data['EMA_26']

        if is_after_market_close_now:
            last_row = stock_data.iloc[-1]
        else:
            last_row = stock_data.iloc[-2]

        if last_row.isnull().any():
            print(f"파생변수 계산에 필요한 데이터가 부족하여 '{stock_name}'을(를) 건너뜁니다.")
            continue

        input_data = pd.DataFrame([[
            last_row['Volume'], last_row['Open'], last_row['Low'],
            last_row['MA_5'], last_row['Volume_MA_10'], last_row['Volatility'],
            last_row['EMA_12'], last_row['MACD']
        ]], columns=[
            'Volume', 'Open', 'Low', 'MA_5', 'Volume_MA_10', 'Volatility', 'EMA_12', 'MACD'
        ])

        scaler_path = os.path.join(BASE_DIR, 'scaler', f'm_{stock_name}_scaler.pkl')

        if not os.path.exists(scaler_path):
            print(f"해당 주식 '{stock_name}'에 대한 스케일러를 찾을 수 없습니다.")
            continue

        scaler = joblib.load(scaler_path)

        scaled_data = scaler.transform(input_data)

        try:
            proba = model.predict_proba(scaled_data)[0][1]
        except Exception as e:
            print(f"예측 중 오류가 발생했습니다: {str(e)}")
            continue

        prediction = 1 if proba >= 0.87 else 0

        # 어제 데이터가 있고 오늘 데이터가 없으며, 장이 열려있는 상태라면 어제 데이터를 업데이트
        existing_record = minusPredict.objects.filter(stock_name=stock_name, created_at=today).first()

        if existing_record:
            if not is_after_market_close_now:
                if existing_record.is_after_market_close:
                    existing_record.created_at = today
                    existing_record.is_after_market_close = False
                    existing_record.save()
            else:
                print(f"'{stock_name}'의 데이터가 이미 존재합니다.")
        else:
            minusPredict.objects.create(
                stock_name=stock_name,
                stock_code=stock_code,
                prediction=prediction,
                created_at=today,
                is_after_market_close=is_after_market_close_now
            )

    print("모든 주식에 대한 예측이 완료되었습니다.")
