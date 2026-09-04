from datetime import datetime, time
import pytz

# Timezones
TZ_IST = pytz.timezone("Asia/Kolkata")
TZ_EST = pytz.timezone("America/New_York")
TZ_UTC = pytz.UTC

# Asset class mapping
INDIAN_ASSETS = {
    "^NSEI", "^BSESN", "^NSEBANK",
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "BHARTIARTL.NS"
}
METALS_ENERGY = {"GLD", "GC=F", "SLV", "SI=F", "USO", "CL=F", "UNG", "NG=F"}
FOREX_ASSETS = {"USDINR=X", "EURUSD=X", "DX-Y.NYB"}
CRYPTO_ASSETS = {"BTC-USD", "ETH-USD"}
US_ASSETS = {"SPY", "QQQ", "XLF", "XLE", "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"}

# Common Indian holidays (approx list / weekends)
INDIAN_HOLIDAYS_2026 = {
    "2026-01-26", "2026-03-03", "2026-03-25", "2026-04-14", "2026-05-01",
    "2026-08-15", "2026-10-02", "2026-10-20", "2026-11-08", "2026-12-25"
}

# US Holidays 2026
US_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25"
}

def is_market_open(ticker: str, dt_utc: datetime | None = None) -> dict:
    """
    Determines if the exchange for a given asset is currently active.
    Returns comprehensive timezone metadata, current local time, and session status.
    """
    if dt_utc is None:
        dt_utc = datetime.now(TZ_UTC)
    elif dt_utc.tzinfo is None:
        dt_utc = TZ_UTC.localize(dt_utc)

    # 1. Crypto is always open (24/7/365)
    if ticker in CRYPTO_ASSETS or "BTC" in ticker or "ETH" in ticker:
        return {
            "is_open": True,
            "exchange": "Binance / Global Crypto",
            "timezone_id": "UTC",
            "timezone_code": "UTC",
            "utc_offset_hours": 0.0,
            "local_time": dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "session": "Continuous 24/7/365",
            "status_message": "24/7 Continuous Trading Session Active"
        }

    # 2. Indian Equities & Indices (NSE / BSE) -> 09:15 - 15:30 IST (Mon-Fri)
    if ticker in INDIAN_ASSETS or ticker.endswith(".NS") or ticker.startswith("^NSE") or ticker.startswith("^BSE"):
        now_ist = dt_utc.astimezone(TZ_IST)
        date_str = now_ist.strftime("%Y-%m-%d")
        weekday = now_ist.weekday()  # 0 is Monday, 6 is Sunday
        
        is_weekday = weekday < 5
        not_holiday = date_str not in INDIAN_HOLIDAYS_2026
        market_start = time(9, 15)
        market_end = time(15, 30)
        current_time = now_ist.time()
        
        is_open = is_weekday and not_holiday and (market_start <= current_time <= market_end)
        
        if is_open:
            status_msg = "NSE Regular Trading Session Active (09:15 - 15:30 IST)"
        elif is_weekday and not_holiday and current_time < market_start:
            status_msg = f"Pre-Market / Opens today at 09:15 IST (Local: {now_ist.strftime('%H:%M:%S')} IST)"
        elif is_weekday and not_holiday and current_time > market_end:
            status_msg = "NSE Market Closed (Post-Market Session / Opens tomorrow 09:15 IST)"
        else:
            status_msg = "NSE Market Closed (Weekend / Holiday - Opens Monday 09:15 IST)"

        return {
            "is_open": is_open,
            "exchange": "NSE / BSE (National Stock Exchange of India)",
            "timezone_id": "Asia/Kolkata",
            "timezone_code": "IST",
            "utc_offset_hours": 5.5,
            "local_time": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "session": "09:15 - 15:30 IST (Mon-Fri)",
            "status_message": status_msg
        }

    # 3. Commodities / MCX -> 09:00 - 23:30 IST (Mon-Fri)
    if ticker in METALS_ENERGY:
        now_ist = dt_utc.astimezone(TZ_IST)
        weekday = now_ist.weekday()
        is_weekday = weekday < 5
        market_start = time(9, 0)
        market_end = time(23, 30)
        current_time = now_ist.time()
        is_open = is_weekday and (market_start <= current_time <= market_end)

        if is_open:
            status_msg = "MCX Commodities Session Active (09:00 - 23:30 IST)"
        else:
            status_msg = "MCX Closed (Opens Mon-Fri 09:00 IST)"

        return {
            "is_open": is_open,
            "exchange": "MCX India / NYMEX Commodities",
            "timezone_id": "Asia/Kolkata",
            "timezone_code": "IST",
            "utc_offset_hours": 5.5,
            "local_time": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "session": "09:00 - 23:30 IST (Mon-Fri)",
            "status_message": status_msg
        }

    # 4. Forex -> Mon 00:00 UTC to Fri 21:00 UTC (24/5 Interbank)
    if ticker in FOREX_ASSETS:
        weekday = dt_utc.weekday()
        if weekday == 5:  # Saturday
            is_open = False
        elif weekday == 6 and dt_utc.time() < time(21, 0):  # Sunday before open
            is_open = False
        elif weekday == 4 and dt_utc.time() > time(22, 0):  # Friday after close
            is_open = False
        else:
            is_open = True

        status_msg = "Global 24/5 Interbank Forex Session Active" if is_open else "Forex Weekend Interbank Closed (Opens Sunday 21:00 UTC)"
            
        return {
            "is_open": is_open,
            "exchange": "Global Forex Interbank (24/5)",
            "timezone_id": "UTC",
            "timezone_code": "UTC",
            "utc_offset_hours": 0.0,
            "local_time": dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "session": "24/5 Interbank (Mon-Fri)",
            "status_message": status_msg
        }

    # 5. US Equities & Sector ETFs -> 09:30 - 16:00 EDT/EST (Mon-Fri)
    now_est = dt_utc.astimezone(TZ_EST)
    date_str = now_est.strftime("%Y-%m-%d")
    weekday = now_est.weekday()
    is_weekday = weekday < 5
    not_holiday = date_str not in US_HOLIDAYS_2026
    market_start = time(9, 30)
    market_end = time(16, 0)
    current_time = now_est.time()
    
    is_open = is_weekday and not_holiday and (market_start <= current_time <= market_end)
    tz_name = now_est.strftime("%Z")  # EDT or EST

    if is_open:
        status_msg = f"NYSE / NASDAQ Regular Session Active (09:30 - 16:00 {tz_name})"
    elif is_weekday and not_holiday and current_time < market_start:
        status_msg = f"US Pre-Market (Opens today at 09:30 {tz_name} / Local: {now_est.strftime('%H:%M:%S')} {tz_name})"
    elif is_weekday and not_holiday and current_time > market_end:
        status_msg = f"US After-Hours / Market Closed (Opens tomorrow 09:30 {tz_name})"
    else:
        status_msg = f"US Markets Closed (Weekend / Holiday - Opens Monday 09:30 {tz_name})"

    return {
        "is_open": is_open,
        "exchange": "NYSE / NASDAQ (US Equities & ETFs)",
        "timezone_id": "America/New_York",
        "timezone_code": tz_name,
        "utc_offset_hours": -4.0 if tz_name == "EDT" else -5.0,
        "local_time": now_est.strftime(f"%Y-%m-%d %H:%M:%S {tz_name}"),
        "session": f"09:30 - 16:00 {tz_name} (Mon-Fri)",
        "status_message": status_msg
    }
