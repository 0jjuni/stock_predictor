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
