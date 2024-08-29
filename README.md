
## 코스피 종목 리스트 불러오기
- shell에 접속하여 아래의 코드를 실행하면 코스피 종목의 리스트를 불러옵니다.
- `python manage.py shell`
- DB를 구축하고 1번만 실행하면 종목 예측 탭을 편하게 사용 가능합니다.
```commandline
from base.utils import load_kospi_stocks  

load_kospi_stocks()
```

## 추천 작업 실행
- shell에 접속하여 아래의 코드를 실행하면 해당 날짜의 추천 작업을 진행한다.
- `python manage.py shell`
- 해당작업은 하루에 1번만 실행하면 user가 사용하는데 문제가 발생하지 않으나 작업을 실행하지 않을 경우 첫 이용자가 약 6분정도의 대기시간을 가져야 접속이 가능하다.
```commandline
from recommendation.views import recommend_stocks

recommend_stocks()
```


## -5%에 대한 예측
```commandline

from base.utils import predict_and_save_stocks  # 실제 앱 이름으로 변경

predict_and_save_stocks()
```