
## Poetry
- 의존성 관리를 위해 poetry를 사용
- XGBoost의 모델과 MinMaxScaler 등을 pkl 파일로 다운 받아 사용했기 때문에 버전이 같아야 돌아가기 때문
```commandline
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python3 -
```
1. 해당 코드를 통해 poetry를 설치한다.
```commandline
poetry install
```
2. 해당 명령어를 Terminal에 입력하여 가상환경을 설치한다.
```commandline
poetry shell
```
3. 해당 명령어를 통해 가상환경을 켠다.
4. setting.py에서 DB에 대한 설정을 한다.
```commandline
python manage.py makemigrations
python manage.py migrate
```
5. 해당 명령어를 통해 DB를 구축한다.

## 코스피 종목 리스트 DB에 불러오기
- shell에 접속하여 아래의 코드를 실행하면 코스피 종목의 리스트를 불러옵니다.
- `python manage.py shell`
- DB를 구축하고 1번만 실행하면 종목 예측 탭을 편하게 사용 가능합니다.
```commandline
from base.utils import load_kospi_stocks  

load_kospi_stocks()
```

## 추천 작업 실행 (DB에 불러오기)
- shell에 접속하여 아래의 코드를 실행하면 해당 날짜의 추천 작업을 진행한다.
- `python manage.py shell`
- 해당작업은 하루에 1번만 실행하면 user가 사용하는데 문제가 발생하지 않으나 작업을 실행하지 않을 경우 첫 이용자가 약 6분정도의 대기시간을 가져야 접속이 가능하다.
```commandline
from recommendation.views import recommend_stocks

recommend_stocks()
```


## -5%에 대한 예측 (DB에 불러오기)
- shell에 접속하여 아래의 코드를 실행하면 해당 날짜의 추천 작업을 진행한다.
- `python manage.py shell`
```commandline

from base.utils import predict_and_save_stocks  # 실제 앱 이름으로 변경

predict_and_save_stocks()
```