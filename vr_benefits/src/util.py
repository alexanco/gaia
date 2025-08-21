import pandas as pd
from datetime import datetime, date, timedelta
from typing import Tuple

DATE_FMT_IN = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"]

def parse_date(x):
    if pd.isna(x):
        return None
    if isinstance(x, (datetime, date)):
        return datetime(x.year, x.month, x.day)
    s = str(x).strip()
    if not s:
        return None
    for f in DATE_FMT_IN:
        try:
            dt = datetime.strptime(s, f)
            return datetime(dt.year, dt.month, dt.day)
        except Exception:
            pass
    # Excel serial (melhor esforço)
    try:
        return datetime.fromordinal(datetime(1899,12,30).toordinal() + int(float(s)))
    except Exception:
        return None

def month_bounds(year: int, month: int) -> Tuple[datetime, datetime]:
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year+1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month+1, 1) - timedelta(days=1)
    return start, end

def intersect_days(beg: datetime, end: datetime, ibeg: datetime, iend: datetime) -> int:
    # Dias em comum entre [beg,end] e [ibeg,iend] (ambos inclusivos).
    if not all([beg, end, ibeg, iend]):
        return 0
    a1 = max(beg, ibeg); a2 = min(end, iend)
    if a1 > a2:
        return 0
    return (a2 - a1).days + 1
