
## 추천 작업 실행
- shell에 접속하여 아래의 코드를 실행하면 해당 날짜의 추천 작업을 진행한다.
- `python manage.py shell`

```python manage.py shell
from recommendation.views import recommend_stocks
recommend_stocks()
```