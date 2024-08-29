from django.shortcuts import render

def home(request):
    return render(request, 'base/home.html')

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
