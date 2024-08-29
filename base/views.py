from django.shortcuts import render

def home(request):
    return render(request, 'base/home.html')

def model_performance(request):
    # 모델 성능 지표 (예시 값)
    performance_data = {
        'accuracy': 0.96,
        'precision': 0.72,
        'recall': 0.90,
        'f1_score': 0.91,
    }

    return render(request, 'base/model_performance.html', performance_data)
