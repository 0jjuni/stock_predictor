import FinanceDataReader as fdr
from .models import Stock  #

def load_kospi_stocks():
    """Load KOSPI stock data into the database."""
    # KOSPI 종목 리스트 가져오기
    kospi_list = fdr.StockListing('Kospi')

    # 데이터베이스에 저장
    for _, row in kospi_list.iterrows():
        Stock.objects.update_or_create(
            code=row['Code'],
            defaults={'name': row['Name']}
        )

    print("KOSPI 종목들이 성공적으로 DB에 연결되었습니다.")


import os
import joblib
import pandas as pd
import FinanceDataReader as fdr
from django.utils.timezone import localdate
from base.models import Stock  # 실제 앱 이름으로 변경하세요.
from predictions.models import Predict_5  # Predict_5 모델 임포트

# 프로젝트의 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 경로를 설정합니다.
model_path = os.path.join(BASE_DIR, 'models', 'minus5per.pkl')

# 모델 로드 (첫 요청 시 한 번만 로드)
model = joblib.load(model_path)

def predict_and_save_stocks():
    today = localdate()  # 오늘 날짜 가져오기

    # 데이터베이스에서 주식 리스트를 가져옴
    stocks = Stock.objects.all()

    # 기존에 저장된 오늘 날짜의 예측 결과 삭제 (재실행 방지)
    Predict_5.objects.filter(created_at=today).delete()

    # 각 주식에 대해 예측을 수행하고 결과를 저장
    for stock in stocks:
        stock_name = stock.name
        stock_code = stock.code

        # 해당 주식의 데이터를 가져옴
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

        # 가장 최근 데이터 선택
        last_row = stock_data.iloc[-1]
        if last_row.isnull().any():
            print(f"파생변수 계산에 필요한 데이터가 부족하여 '{stock_name}'을(를) 건너뜁니다.")
            continue

        # 필요한 열 선택
        input_data = pd.DataFrame([[
            last_row['Close'], last_row['Volume'], last_row['Open'], last_row['High'], last_row['Low'],
            last_row['MA_5'], last_row['Volume_MA_10'], last_row['Volatility'],
            last_row['EMA_12'], last_row['MACD']
        ]], columns=[
            'Volume', 'Open', 'Low', 'MA_5', 'Volume_MA_10', 'Volatility', 'EMA_12', 'MACD'
        ])

        # Scaler 파일 경로 설정 및 로드
        scaler_path = os.path.join(BASE_DIR, 'scaler', f'm_{stock_name}_scaler.pkl')

        if not os.path.exists(scaler_path):
            print(f"해당 주식 '{stock_name}'에 대한 스케일러를 찾을 수 없습니다.")
            continue

        scaler = joblib.load(scaler_path)

        # 스케일링
        scaled_data = scaler.transform(input_data)

        # 예측 확률 수행
        try:
            proba = model.predict_proba(scaled_data)[0][1]  # 클래스 1의 확률
        except Exception as e:
            print(f"예측 중 오류가 발생했습니다: {str(e)}")
            continue

        # 확률이 0.87 이상인 경우에만 1로 설정
        prediction = 1 if proba >= 0.87 else 0

        # 예측 결과를 Predict_5 모델에 저장
        Predict_5.objects.create(
            stock_name=stock_name,
            stock_code=stock_code,
            prediction=prediction,
            created_at=today
        )

    print("모든 주식에 대한 예측이 완료되었습니다.")
