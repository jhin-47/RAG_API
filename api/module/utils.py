
# - SQLite DB 파일명 규칙(v1) `RAGDB_{날짜-YYYYMMDD}_{시간-HHMM}_{source}_{model}_nrows{행 개수}_njobs{채용공고수}.sqlite`
import datetime

def get_db_filename(source: str, model: str, nrows: int, njobs: int, string: str = "") -> str:
    """SQLite DB 파일명을 생성함
    
    Args:
        source (str): 데이터 수집 소스명
        model (str): 사용한 모델명
        nrows (int): 행 개수
        njobs (int): 채용공고 수
        string (str, optional): 파일명 맨 뒤에 붙을 텍스트. 기본값은 ""임
    
    Returns:
        str: 생성된 DB 파일명
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    if string:
        db_filename = f"RAGDB_{date_str}_{time_str}_{source}({model})_nrows{nrows}_njobs{njobs}_{string}.sqlite"
    else:
        db_filename = f"RAGDB_{date_str}_{time_str}_{source}({model})_nrows{nrows}_njobs{njobs}.sqlite"
    db_filename = db_filename.replace("/", "_")
    return db_filename

