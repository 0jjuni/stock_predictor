import os
import joblib
from django.shortcuts import render
from django.http import HttpResponseBadRequest
import FinanceDataReader as fdr

# 프로젝트의 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 경로를 설정합니다.
model_path = os.path.join(BASE_DIR, 'models', '1day5per.pkl')

# 모델 로드 (첫 요청 시 한 번만 로드)
model = joblib.load(model_path)


def predict_stock(request):
    if request.method == 'POST':
        try:
            # 사용자가 입력한 주식명 가져오기
            stock_name = request.POST.get('stock_name').strip()

            # Kospi 종목 리스트에서 해당 주식명의 코드를 찾기
            kospi_list = fdr.StockListing('Kospi')
            stock_info = kospi_list[kospi_list['Name'] == stock_name]

            if stock_info.empty:
                return HttpResponseBadRequest(f"Stock name '{stock_name}' not found in KOSPI listings.")

            stock_code = stock_info['Code'].values[0]

            # 해당 주식의 데이터를 가져옴
            stock_data = fdr.DataReader(stock_code)

            if stock_data.empty:
                return HttpResponseBadRequest(f"해당 주식 {'{stock_name}'}은 지원하지 않습니다.")

            # 데이터프레임의 마지막 행(가장 최근 데이터)에서 필요한 열 추출
            last_row = stock_data.iloc[-1]
            open_price = last_row['Open']
            high = last_row['High']
            low = last_row['Low']
            close = last_row['Close']
            volume = last_row['Volume']

            # Scaler 파일 경로 설정
            scaler_path = os.path.join(BASE_DIR, 'scaler', f'{stock_name}_scaler.pkl')

            # Scaler 로드
            if not os.path.exists(scaler_path):
                return HttpResponseBadRequest(f"해당 주식 {'{stock_name}'}은 지원하지 않습니다.")

            scaler = joblib.load(scaler_path)

            # 입력 데이터를 스케일링
            input_data = [[close, volume, open_price, high, low]]
            scaled_data = scaler.transform(input_data)

            # 예측 수행
            prediction = model.predict(scaled_data)[0]

            # 예측 결과와 추가 정보를 새로운 템플릿에 전달하여 렌더링
            context = {
                'stock_name': stock_name,
                'open_price': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume,
                'prediction': prediction,
            }
            return render(request, 'predictions/prediction_result.html', context)
        except (KeyError, ValueError, IndexError) as e:
            return HttpResponseBadRequest(f"Error during prediction: {str(e)}")

    return render(request, 'predictions/predict.html')
