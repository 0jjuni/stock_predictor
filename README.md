
## 코스피 종목 리스트 불러오기
- shell에 접속하여 아래의 코드를 실행하면 코스피 종목의 리스트를 불러옵니다.
- `python manage.py shell`
- DB를 구축하고 1번만 실행하면 종목 예측 탭을 편하게 사용 가능합니다.
```commandline
from base.utils import load_kospi_stocks  # utils.py 파일에서 함수 불러오기

# 함수 실행
load_kospi_stocks()
```

## 추천 작업 실행
- shell에 접속하여 아래의 코드를 실행하면 해당 날짜의 추천 작업을 진행한다.
- `python manage.py shell`

```commandline
from recommendation.views import recommend_stocks
recommend_stocks()
```