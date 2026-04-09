import streamlit as st
import webbrowser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone, date
import urllib.parse
import time
import pandas as pd
import math
import re
import streamlit.components.v1 as components
import concurrent.futures
import os
import json
import xml.etree.ElementTree as ET

# ==========================================
# 依賴套件檢查與匯入
# ==========================================
try:
    import googlemaps
except ImportError:
    googlemaps = None

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

try:
    import altair as alt
except ImportError:
    alt = None

try:
    from lunarcalendar import Converter, Solar, Lunar
except ImportError:
    Converter = None
    Solar = None
    Lunar = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    webdriver = None


# ==========================================
# 設定：Google Maps API Key
# ==========================================
GOOGLE_MAPS_API_KEY = "AIzaSyBK2mfGSyNnfytW7sRkNM5ZWqh2SVGNabo" 

# ==========================================
# Streamlit 頁面設定 (必須是第一個 Streamlit 指令)
# ==========================================
st.set_page_config(
    page_title="宸竹專屬工具箱",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS 樣式注入
# ==========================================
st.markdown("""
    <style>
    /* === 強制全域背景與文字顏色 === */
    .stApp {
        background-color: #f5f5f5;
    }
    
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, li, span, div {
        color: #333333;
    }

    /* === 針對 Streamlit Tabs (分頁) === */
    button[data-baseweb="tab"] div p {
        color: #000000 !important; 
        font-weight: bold;
        font-size: 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p {
        color: #e74c3c !important;
    }
    
    /* === 標題樣式 === */
    .main-title {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 40px; 
        font-weight: bold;
        text-align: center;
        color: #000000 !important;
        margin-bottom: 10px;
    }
    .section-title {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 28px; 
        font-weight: bold;
        color: #000000 !important;
        margin-top: 5px;
        margin-bottom: 5px;
        border-bottom: 2px solid #ccc;
    }
    
    /* === 數據框與卡片樣式 === */
    .data-box {
        background-color: #2c3e50;
        padding: 15px;
        border-radius: 5px;
        font-family: "Consolas", "Microsoft JhengHei", sans-serif; 
        font-size: 28px; 
        font-weight: bold;
        line-height: 1.5;
        margin-bottom: 10px;
        color: #ecf0f1 !important; 
    }

    .traffic-card {
        background-color: #2c3e50;
        border: 1px solid #546E7A;
        border-radius: 4px;
        padding: 10px 15px;
        margin-bottom: 12px;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .traffic-card-title {
        color: #ecf0f1 !important;
        font-size: 22px; 
        font-weight: normal;
        margin-bottom: 8px;
        border-bottom: 1px solid #455a64;
        display: inline-block;
        padding-right: 10px;
        padding-bottom: 2px;
    }
    .traffic-row {
        display: block;
        font-size: 28px; 
        font-weight: bold;
        margin-bottom: 5px;
        text-decoration: none !important;
    }
    .traffic-row:hover {
        opacity: 0.8;
    }

    /* === 顏色定義 === */
    .text-gold { color: #ffca28 !important; }
    .text-cyan { color: #26c6da !important; }
    .text-green { color: #2ecc71 !important; } 
    .text-red { color: #ff5252 !important; }   
    .text-white { color: #ffffff !important; }
    
    .data-box span, .traffic-card span {
        color: inherit;
    }

    .stButton>button {
        font-family: "Microsoft JhengHei", sans-serif;
        font-weight: bold;
        border-radius: 5px;
    }

    /* === 家族時光樣式 === */
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    div[data-testid="stMetricLabel"] label {
        color: #555 !important;
        font-size: 18px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 36px !important;
    }

    .birthday-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #ff4b4b;
    }
    .big-font {
        font-size: 26px !important; 
        font-weight: bold;
        color: #333 !important;
    }
    .sub-font {
        font-size: 18px; 
        color: #555 !important;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .highlight {
        color: #ff4b4b !important;
        font-weight: bold;
        font-size: 22px; 
    }
    .top-card-highlight {
        border-left: 8px solid #ff4b4b !important;
        background-color: #fff9f9 !important;
        border: 1px solid #ffebeb;
    }
    
    div[data-testid="stToolbar"] {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 5px;
    }
    
    /* 交通方式分類標題 */
    .traffic-section-header {
        font-size: 22px;
        font-weight: bold;
        color: #333;
        margin-top: 15px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* === 單獨針對公車動態的按鈕 (310/952) 放大字體 === */
    a[href*="ebus.gov.taipei"] p {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    
    /* === 資訊欄卡片樣式 === */
    .info-panel-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #005A9C;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 15px;
    }
    .info-text-large {
        font-size: 22px !important;
        color: #1a1a1a !important;
        line-height: 1.6;
        margin-bottom: 8px;
        font-weight: bold;
    }
    .info-text-normal {
        font-size: 20px !important;
        color: #333333 !important;
        line-height: 1.5;
        margin-bottom: 6px;
    }
    .info-label {
        color: #005A9C;
        font-weight: 900;
    }

    /* === 新增的高級質感天氣顯示 === */
    .weather-premium-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 12px;
        padding: 16px;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin: 12px 0;
        display: flex;
        flex-direction: column;
    }
    .weather-premium-card span, .weather-premium-card div {
        color: #ffffff !important;
    }
    .weather-premium-title {
        font-size: 15px;
        color: #b3cce6 !important;
        margin-bottom: 6px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .weather-premium-data {
        font-size: 20px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* === 為 iPhone 15 重新優化的專屬時間資訊卡片 === */
    .time-premium-box {
        background-color: #ffffff;
        border-left: 8px solid #ffb300;
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .time-row {
        font-size: 24px; /* 適合 iPhone 15 的大字體 */
        color: #333333;
        margin-bottom: 10px;
        font-weight: 700;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f5f5f5;
        padding-bottom: 8px;
    }
    .time-row:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .time-label {
        color: #555555;
        font-size: 20px;
    }
    .time-value {
        font-size: 24px;
    }
    .live-link-btn {
        display: inline-block;
        margin-top: 10px;
        padding: 14px 24px;
        color: white !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    .live-link-btn:hover {
        opacity: 0.8;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 邏輯功能函式庫 (工具類)
# ==========================================

# 全域定義台灣時區，確保全面統一
TW_TZ = timezone(timedelta(hours=8))

def get_time_str(dt):
    return dt.strftime("%H:%M:%S")

@st.cache_data(ttl=3600)
def get_airport_news(dest_city):
    """取得特定機場/地點的公開新聞資訊，優先包含2則天氣新聞，總共顯示5則(僅限當天)"""
    import email.utils
    
    # 【關鍵修正 1】：新聞 API 絕對不能用代理，必須用最原生的 requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    today_date = datetime.now(TW_TZ).date()
    
    def fetch_google_news(query, limit):
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            root = ET.fromstring(res.text)
            news_list = []
            for item in root.findall('.//item'):
                try:
                    pub_date_str = item.find('pubDate').text
                    if pub_date_str:
                        pub_dt = email.utils.parsedate_to_datetime(pub_date_str)
                        pub_dt_tw = pub_dt.astimezone(TW_TZ)
                        if pub_dt_tw.date() != today_date:
                            continue 
                except Exception:
                    pass 
                
                title = item.find('title').text
                link = item.find('link').text
                news_list.append({"title": title, "link": link})
                if len(news_list) >= limit:
                    break
            return news_list
        except:
            return []

    weather_news = fetch_google_news(f"{dest_city} 天氣", 2)
    general_news = fetch_google_news(f"{dest_city} 航空 OR 旅遊 OR 機場", 5)
    
    final_news = []
    seen_links = set()
    
    for n in weather_news:
        final_news.append(n)
        seen_links.add(n['link'])
        
    for n in general_news:
        if len(final_news) >= 5:
            break
        if n['link'] not in seen_links:
            final_news.append(n)
            seen_links.add(n['link'])
            
    return final_news

# 航廈中英對照表
TERMINAL_INFO = {
    "TPE": "桃園國際機場 (第2航廈)",
    "TSA": "台北松山機場 (第1航廈)",
    "KHH": "高雄國際機場 (國際線航廈)",
    "YVR": "溫哥華國際機場 (主航廈)",
    "CTS": "札幌新千歲機場 (國際線航廈)",
    "OKA": "沖繩那霸機場 (國際線航廈)",
    "KIX": "大阪關西國際機場 (第1航廈)",
    "KMQ": "小松機場 (國際線航廈)",
    "ICN": "首爾仁川國際機場 (第1航廈)",
    "CGK": "雅加達蘇加諾-哈達機場 (第3航廈)",
    "PNH": "金邊國際機場 (國際線航廈)",
    "MNL": "馬尼拉國際機場 (第1航廈)",
    "DAD": "峴港國際機場 (第2航廈)",
    "HAN": "河內內排國際機場 (第2航廈)",
    "PVG": "上海浦東國際機場 (第2航廈)",
    "HGH": "杭州蕭山國際機場 (第4航廈)",
    "TFU": "成都天府國際機場 (第1航廈)",
    "SHA": "上海虹橋國際機場 (第1航廈)",
    "MFM": "澳門國際機場 (客運大樓)",
    "HKG": "香港國際機場 (第1航廈)"
}

AIRPORT_COORDS = {
    "TPE": (25.0797, 121.2342), "TSA": (25.0697, 121.5525), "KHH": (22.5771, 120.3500),
    "YVR": (49.1967, -123.1815), "CTS": (42.7752, 141.6923), "OKA": (26.1958, 127.6458),
    "KIX": (34.4320, 135.2304), "KMQ": (36.3940, 136.4069), "ICN": (37.4602, 126.4407),
    "CGK": (-6.1256, 106.6558), "PNH": (11.5466, 104.8443), "MNL": (14.5090, 121.0194),
    "DAD": (16.0439, 108.1993), "HAN": (21.2187, 105.8042), "PVG": (31.1443, 121.8083),
    "HGH": (30.2295, 120.4345), "TFU": (30.3084, 104.4442), "SHA": (31.1979, 121.3363),
    "MFM": (22.1496, 113.5915), "HKG": (22.3080, 113.9185)
}

@st.cache_data(ttl=600)
def get_airport_weather(airport_code):
    coords = AIRPORT_COORDS.get(airport_code)
    if not coords:
        return "暫無該機場天氣資料"
    lat, lon = coords
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,precipitation&timezone=auto"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            temp = data['current'].get('temperature_2m', 'N/A')
            w_code = data['current'].get('weather_code', -1)
            precip = data['current'].get('precipitation', 0)
            
            is_rain = w_code in [51, 53, 55, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99]
            is_snow = w_code in [71, 73, 75, 77, 85, 86]
            
            rain_str = "☔ 有雨" if is_rain else "☁️ 無雨"
            snow_str = "❄️ 有雪" if is_snow else "❌ 無雪"
            
            if precip > 0:
                rain_str += f"({precip}mm)"
                
            return f"🌡️ {temp}°C | {rain_str} | {snow_str}"
        else:
            raise Exception("Open-Meteo API HTTP Error")
    except Exception:
        try:
            fallback_url = f"https://wttr.in/{lat},{lon}?format=%t+%c"
            f_res = requests.get(fallback_url, headers=headers, timeout=10)
            if f_res.status_code == 200:
                return f"🌡️ {f_res.text.strip()} (備用來源)"
        except:
            pass
        return "連線失敗，請稍後重試"

@st.cache_data(ttl=600) 
def get_weather_data_html():
    locations = [
        {"name": "新竹", "lat": 24.805, "lon": 120.985},
        {"name": "板橋", "lat": 25.029, "lon": 121.472},
        {"name": "京樺牛肉麵", "lat": 25.056, "lon": 121.526},
        {"name": "長榮航空", "lat": 25.042, "lon": 121.296},
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    result_html = ""
    for loc in locations:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&current=temperature_2m,weather_code&hourly=precipitation_probability&timezone=auto&forecast_days=1"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                temp = data['current'].get('temperature_2m', 'N/A')
                w_code = data['current'].get('weather_code', -1)
                
                icon = ""
                rain_text = ""
                try:
                    current_time_str = data['current']['time']
                    try:
                        cur_dt = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M")
                    except ValueError:
                        cur_dt = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%S")
                    
                    cur_hour_dt = cur_dt.replace(minute=0, second=0)
                    search_time = cur_hour_dt.strftime("%Y-%m-%dT%H:%M")
                    hourly_times = data['hourly']['time']
                    
                    if search_time in hourly_times:
                        idx = hourly_times.index(search_time)
                        future_probs = data['hourly']['precipitation_probability'][idx : idx+5]
                        
                        if future_probs:
                            max_prob = max(future_probs)
                            is_snow_code = w_code in [56, 57, 66, 67, 71, 73, 75, 77, 85, 86]
                            is_thunder_code = w_code in [95, 96, 99]

                            if is_snow_code:
                                icon = "❄️"
                            elif is_thunder_code:
                                icon = "⛈️"
                            else:
                                if max_prob <= 10: icon = "☀️"
                                elif max_prob <= 40: icon = "☁️"
                                else:
                                    if temp != 'N/A' and temp <= 0: icon = "❄️"
                                    elif max_prob <= 70: icon = "🌦️"
                                    else: icon = "☔"
                            
                            rain_text = f" ({icon}{max_prob}%)"
                except Exception:
                    pass 

                name_display = loc['name']
                if len(name_display) == 2: name_display += " " 
                
                result_html += f"{name_display}: {temp}°C{rain_text}<br>"
            else:
                result_html += f"{loc['name']}: N/A<br>"
        except:
            result_html += f"{loc['name']}: Err<br>"
            
    if not result_html:
        return "暫無氣象資料"
    return result_html

def parse_duration_to_minutes(text):
    try:
        total_mins = 0
        remaining_text = text
        if "小時" in text:
            parts = text.split("小時")
            hours = int(parts[0].strip())
            total_mins += hours * 60
            remaining_text = parts[1]
        if "分鐘" in remaining_text:
            mins_part = remaining_text.replace("分鐘", "").strip()
            if mins_part.isdigit():
                total_mins += int(mins_part)
        return total_mins
    except:
        return 0

def get_google_maps_url(start, end, mode='driving'):
    s_enc = urllib.parse.quote(start)
    e_enc = urllib.parse.quote(end)
    
    if mode == 'transit':
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=transit"
    elif mode == 'bicycling':
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=bicycling"
    elif mode == 'two_wheeler':
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=two-wheeler&avoid=highways,tolls"
    else:
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=driving"

def calculate_traffic(gmaps, start_addr, end_addr, std_time, label_prefix, mode='driving'):
    url = get_google_maps_url(start_addr, end_addr, mode=mode)
    
    if not gmaps:
        return f"{label_prefix}: API未設定", "text-white", url

    try:
        kwargs = {
            'origins': start_addr,
            'destinations': end_addr,
            'departure_time': datetime.now(TW_TZ),
            'language': 'zh-TW'
        }
        
        if mode == 'two_wheeler':
            kwargs['mode'] = 'driving'
            kwargs['avoid'] = 'highways'
        else:
            kwargs['mode'] = mode

        matrix = gmaps.distance_matrix(**kwargs)
        
        if matrix.get('status') != 'OK' or not matrix.get('rows'):
            return f"{label_prefix}: 查無路線", "text-white", url

        el = matrix['rows'][0]['elements'][0]
        
        if el.get('status') != 'OK':
            time_str = "無法估算"
            dist_str = ""
        else:
            if 'duration_in_traffic' in el:
                time_str = el['duration_in_traffic']['text']
            elif 'duration' in el:
                time_str = el['duration']['text']
            else:
                time_str = "無法估算"
                
            if 'distance' in el:
                dist_str = el['distance']['text']
                dist_str = dist_str.replace(" 公里", "km").replace("公里", "km").replace(" km", "km")
            else:
                dist_str = ""
            
        cur_mins = parse_duration_to_minutes(time_str)
        
        if cur_mins >= 60:
            h = cur_mins // 60
            m = cur_mins % 60
            time_display = f"{h}小時{m}分" if m > 0 else f"{h}小時"
        elif cur_mins > 0:
            time_display = f"{cur_mins}分"
        else:
            time_display = time_str.replace("分鐘", "分").replace(" ", "")
        
        if "往板橋" in label_prefix or "反板橋" in label_prefix or "反江子翠" in label_prefix:
            base_class = "text-gold"
        else:
            base_class = "text-cyan"
            
        if cur_mins > 0:
            diff = cur_mins - std_time
            sign = "+" if diff >= 0 else "" 
            
            if diff > 20:
                diff_part = f"<span style='color: #ff5252 !important;'>({sign}{diff}分)</span>"
            else:
                diff_part = f"({sign}{diff}分)"
            
            display_text = f"{label_prefix}: {time_display} {diff_part} {dist_str}".strip()
            color_class = base_class 
            
        else:
            display_text = f"{label_prefix}: {time_display} {dist_str}".strip()
            color_class = base_class
            
        return display_text, color_class, url
        
    except Exception as e:
        return f"{label_prefix}: 查詢失敗", "text-white", url

# ==========================================
# 邏輯功能函式庫 (家族時光類)
# ==========================================
def get_western_zodiac(day, month):
    zodiac_signs = [
        (1, 20, "摩羯座"), (2, 19, "水瓶座"), (3, 20, "雙魚座"), (4, 20, "白羊座"),
        (5, 20, "金牛座"), (6, 21, "雙子座"), (7, 22, "巨蟹座"), (8, 23, "獅子座"),
        (9, 23, "處女座"), (10, 23, "天秤座"), (11, 22, "天蠍座"), (12, 22, "射手座"),
        (12, 31, "摩羯座")
    ]
    for m, d, sign in zodiac_signs:
        if (month == m and day <= d) or (month == m - 1 and day > d and not (m == 1 and day <= 20)):
            return sign
    return "摩羯座"

def get_chinese_zodiac(year):
    zodiacs = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]
    return zodiacs[(year - 4) % 12]

def calculate_detailed_age(birth_date):
    today = datetime.now(TW_TZ).date()
    delta = today - birth_date
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years, delta.days

def get_lunar_date_str(birth_date):
    try:
        if Converter and Solar:
            solar = Solar(birth_date.year, birth_date.month, birth_date.day)
            lunar = Converter.Solar2Lunar(solar)
            return f"{lunar.month}/{lunar.day}"
        else:
            return "N/A"
    except Exception:
        return "N/A"

def get_next_birthday_days(birth_date):
    today = datetime.now(TW_TZ).date()
    this_year_bday = date(today.year, birth_date.month, birth_date.day)
    if this_year_bday < today:
        next_bday = date(today.year + 1, birth_date.month, birth_date.day)
    else:
        next_bday = this_year_bday
    return (next_bday - today).days

def get_next_lunar_birthday_days(birth_date):
    try:
        if Converter and Solar and Lunar:
            today = datetime.now(TW_TZ).date()
            solar_birth = Solar(birth_date.year, birth_date.month, birth_date.day)
            lunar_birth = Converter.Solar2Lunar(solar_birth)
            birth_lmonth = lunar_birth.month
            birth_lday = lunar_birth.day
            
            solar_today = Solar(today.year, today.month, today.day)
            lunar_today = Converter.Solar2Lunar(solar_today)
            current_lyear = lunar_today.year
            
            try:
                this_year_lunar = Lunar(current_lyear, birth_lmonth, birth_lday, isleap=False)
                this_year_solar = Converter.Lunar2Solar(this_year_lunar)
                this_year_bday = date(this_year_solar.year, this_year_solar.month, this_year_solar.day)
            except ValueError: 
                this_year_lunar = Lunar(current_lyear, birth_lmonth, birth_lday-1, isleap=False)
                this_year_solar = Converter.Lunar2Solar(this_year_lunar)
                this_year_bday = date(this_year_solar.year, this_year_solar.month, this_year_solar.day)

            if this_year_bday < today:
                next_lyear = current_lyear + 1
                try:
                    next_year_lunar = Lunar(next_lyear, birth_lmonth, birth_lday, isleap=False)
                    next_year_solar = Converter.Lunar2Solar(next_year_lunar)
                    next_bday = date(next_year_solar.year, next_year_solar.month, next_year_solar.day)
                except ValueError:
                    next_year_lunar = Lunar(next_lyear, birth_lmonth, birth_lday-1, isleap=False)
                    next_year_solar = Converter.Lunar2Solar(next_year_lunar)
                    next_bday = date(next_year_solar.year, next_year_solar.month, next_year_solar.day)
            else:
                next_bday = this_year_bday
                
            return (next_bday - today).days
        else:
            return "N/A"
    except Exception:
        return "N/A"

# ==========================================
# 即時 Delay 計算與擷取 API (全面強化版)
# ==========================================
@st.cache_data(ttl=300)
def get_realtime_flight_status(flight_number, std_time_str):
    fa_flight_id = flight_number.upper().replace("BR", "EVA")
    fa_url = f"https://zh-tw.flightaware.com/live/flight/{fa_flight_id}"
    
    # 預設狀態 (若無資料)
    sched_str = std_time_str
    sched_takeoff_str = "無資料"  
    gate_str = "尚未出發"
    delay_mins = "無法計算"
    takeoff_str = "尚未起飛"
    taxi_mins = "無法計算"
    eta_str = "無資料"

    sched_gate_ts = None
    sched_takeoff_ts = None
    act_gate_ts = None
    act_takeoff_ts = None

    fa_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US,en;q=0.8",
    }

    # 1. 深度 JSON 擷取：整合 ScraperAPI + 支援全新 Apollo State 架構
    try:
        # 強制使用家用真實 IP 繞過最高級防護
        SCRAPER_API_KEY = "c84488b98c1d6af5b8b94b306c2e6001"
        payload = {
            'api_key': SCRAPER_API_KEY,
            'url': fa_url,
            'render': 'true',     
            'premium': 'true',    
            'keep_headers': 'true'
        }
        
        fa_res = requests.get('http://api.scraperapi.com', params=payload, headers=fa_headers, timeout=45)
        
        if fa_res.status_code == 200:
            soup = BeautifulSoup(fa_res.text, "html.parser")
            all_flights = []
            
            # 【關鍵強化A】：擷取舊版 Next.js Data
            script_next = soup.find("script", id="__NEXT_DATA__")
            if script_next:
                data = json.loads(script_next.string)
                def extract_flights_next(obj):
                    if isinstance(obj, dict):
                        if "gateDepartureTimes" in obj and "takeoffTimes" in obj:
                            all_flights.append(obj)
                        for k, v in obj.items():
                            extract_flights_next(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_flights_next(item)
                extract_flights_next(data)

            # 【關鍵強化B】：擷取新版 Apollo Client State (解決載入太快取不到的問題)
            if not all_flights:
                scripts = soup.find_all("script")
                for s in scripts:
                    if s.string and "__APOLLO_STATE__" in s.string:
                        match = re.search(r'__APOLLO_STATE__\s*=\s*({.*?});', s.string, re.DOTALL)
                        if match:
                            try:
                                apollo_data = json.loads(match.group(1))
                                for key, val in apollo_data.items():
                                    if isinstance(val, dict) and "gateDepartureTimes" in val and "takeoffTimes" in val:
                                        all_flights.append(val)
                            except:
                                pass
            
            if all_flights:
                today_str = datetime.now(TW_TZ).strftime("%Y-%m-%d")
                best_flight = None
                
                # 篩選最符合當天的航班紀錄
                for fobj in all_flights:
                    s_ts = fobj.get("gateDepartureTimes", {}).get("scheduled") or fobj.get("takeoffTimes", {}).get("scheduled")
                    if s_ts:
                        dt_str = datetime.fromtimestamp(s_ts, TW_TZ).strftime("%Y-%m-%d")
                        if dt_str == today_str:
                            best_flight = fobj
                            break
                if not best_flight and all_flights:
                    best_flight = all_flights[0]

                if best_flight:
                    gate_times = best_flight.get("gateDepartureTimes", {})
                    takeoff_times = best_flight.get("takeoffTimes", {})
                    arr_times = best_flight.get("gateArrivalTimes", {})
                    landing_times = best_flight.get("landingTimes", {})
                    
                    sched_gate_ts = gate_times.get("scheduled")
                    sched_takeoff_ts = takeoff_times.get("scheduled")
                    act_gate_ts = gate_times.get("actual") 
                    act_takeoff_ts = takeoff_times.get("actual")
                    
                    eta = arr_times.get("actual") or arr_times.get("estimated") or landing_times.get("actual") or landing_times.get("estimated") or arr_times.get("scheduled")
                    
                    if sched_gate_ts: sched_str = datetime.fromtimestamp(sched_gate_ts, TW_TZ).strftime("%H:%M")
                    if sched_takeoff_ts: sched_takeoff_str = datetime.fromtimestamp(sched_takeoff_ts, TW_TZ).strftime("%H:%M")
                    if act_gate_ts: gate_str = datetime.fromtimestamp(act_gate_ts, TW_TZ).strftime("%H:%M")
                    if act_takeoff_ts: takeoff_str = datetime.fromtimestamp(act_takeoff_ts, TW_TZ).strftime("%H:%M")
                    if eta: eta_str = datetime.fromtimestamp(eta, TW_TZ).strftime("%H:%M")
                    
                    # 從 Timestamp 精確算出實際滑行時間
                    if act_gate_ts and act_takeoff_ts and act_takeoff_ts > act_gate_ts:
                        taxi_mins = int((act_takeoff_ts - act_gate_ts) / 60)
    except Exception:
        pass

    # 2. 強大備援機制：如果 API 失效，呼叫 Selenium 本機端備援
    if webdriver is not None and (gate_str in ["尚未出發", "無資料", "無閘口資訊"] or takeoff_str in ["尚未起飛", "無資料"]):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            # 【關鍵強化C】：強制指定語系，確保擷取邏輯吻合
            options.add_argument("--lang=zh-TW")
            options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-TW,zh,en-US,en'})
            
            driver = webdriver.Chrome(options=options)
            driver.get(fa_url)
            
            # 【關鍵強化D】：加長等待時間並等待具體文字出現，解決載入太快而擷取失敗的問題
            WebDriverWait(driver, 15).until(
                lambda d: "離開閘口" in d.page_source or "尚未出發" in d.page_source or "Left Gate" in d.page_source or "scheduled" in d.page_source.lower()
            )
            time.sleep(3) 

            # 注入雙語兼容的 JS 腳本
            js_extractor = """
            function extractFlightData() {
                let data = {};
                let divs = document.querySelectorAll('div');
                
                // 找尋出發時間區塊 (支援中英文)
                let depBlock = Array.from(divs).find(el => el.innerText && 
                    ((el.innerText.includes('出發時間') && el.innerText.includes('離開閘口')) || 
                     (el.innerText.includes('Departure Times') && el.innerText.includes('Left Gate')))
                );
                if (depBlock) {
                    let text = depBlock.innerText;
                    
                    let gateMatch = text.match(/(?:離開閘口|Left Gate)[\\s\\n]+(\\d{2}:\\d{2})/);
                    if(gateMatch) data.gate_actual = gateMatch[1];

                    let schedGateMatch = text.match(/(?:計畫|Scheduled)[\\s\\n]+(\\d{2}:\\d{2})/); 
                    if(schedGateMatch) data.gate_sched = schedGateMatch[1];

                    let takeoffMatch = text.match(/(?:起飛|Takeoff)[\\s\\n]+(?:->\\s*)?(\\d{2}:\\d{2})/);
                    if(takeoffMatch) data.takeoff_actual = takeoffMatch[1];

                    let takeoffPart = text.split(/(?:起飛|Takeoff)/)[1] || "";
                    let schedTakeoffMatch = takeoffPart.match(/(?:計畫|Scheduled)[\\s\\n]+(\\d{2}:\\d{2})/);
                    if(schedTakeoffMatch) data.takeoff_sched = schedTakeoffMatch[1];

                    let taxiMatch = text.match(/(?:滑行時間|Taxi Time)[\\s\\n:]+(\\d+)[\\s\\n]*(?:分鐘|m|mins)/);
                    if(taxiMatch) data.taxi = parseInt(taxiMatch[1]);
                }

                // 找尋到達時間區塊
                let arrBlock = Array.from(divs).find(el => el.innerText && 
                    ((el.innerText.includes('到達時間') && (el.innerText.includes('著陸') || el.innerText.includes('到達閘口'))) ||
                     (el.innerText.includes('Arrival Times') && (el.innerText.includes('Landed') || el.innerText.includes('Arrived'))))
                );
                if (arrBlock) {
                    let text = arrBlock.innerText;
                    let arrMatch = text.match(/(?:到達閘口|Arrived at Gate)[\\s\\n]+(?:->\\s*)?(\\d{2}:\\d{2})/);
                    if(!arrMatch) arrMatch = text.match(/(?:著陸|Landed)[\\s\\n]+(?:->\\s*)?(\\d{2}:\\d{2})/);
                    if(arrMatch) data.eta = arrMatch[1];
                }
                return data;
            }
            return extractFlightData();
            """
            extracted_data = driver.execute_script(js_extractor)

            if extracted_data.get('gate_actual') and gate_str in ["尚未出發", "無資料", "無閘口資訊"]:
                gate_str = extracted_data['gate_actual']
                try:
                    h, m = map(int, gate_str.split(':'))
                    act_gate_ts = int(datetime.now(TW_TZ).replace(hour=h, minute=m, second=0).timestamp())
                except: pass
            if extracted_data.get('gate_sched') and sched_str in ["無資料"]:
                sched_str = extracted_data['gate_sched']
                try:
                    h, m = map(int, sched_str.split(':'))
                    sched_gate_ts = int(datetime.now(TW_TZ).replace(hour=h, minute=m, second=0).timestamp())
                except: pass
            if extracted_data.get('takeoff_actual') and takeoff_str in ["尚未起飛", "無資料"]:
                takeoff_str = extracted_data['takeoff_actual']
            if extracted_data.get('takeoff_sched') and sched_takeoff_str in ["無資料"]:
                sched_takeoff_str = extracted_data['takeoff_sched']
            if extracted_data.get('taxi') and taxi_mins == "無法計算":
                taxi_mins = extracted_data['taxi']
            if extracted_data.get('eta') and eta_str == "無資料":
                eta_str = extracted_data['eta']

        except Exception as e:
            pass
        finally:
            if 'driver' in locals():
                driver.quit()

    # 3. 計算 Delay: 實際出發 與 計畫出發的差異 (支援跨夜防呆邏輯)
    if act_gate_ts and sched_gate_ts:
        delay_mins = max(0, int((act_gate_ts - sched_gate_ts) / 60))
    elif gate_str not in ["尚未出發", "無資料", "無閘口資訊"] and sched_str not in ["無資料", "無法計算"]:
        try:
            g_h, g_m = map(int, gate_str.split(':'))
            s_h, s_m = map(int, sched_str.split(':'))
            g_mins = g_h * 60 + g_m
            s_mins = s_h * 60 + s_m
            # 跨夜保護機制 (若表定 23:30 但實際 00:10 出發)
            if g_mins < s_mins and s_h >= 20 and g_h <= 4:
                g_mins += 24 * 60
            delay_mins = max(0, g_mins - s_mins)
        except:
            delay_mins = "無法計算"

    return sched_str, gate_str, delay_mins, sched_takeoff_str, takeoff_str, taxi_mins, eta_str

# ==========================================
# 全局航班常態資料庫 (原始設定基礎)
# ==========================================
MASTER_STATIC_DB = {
    "BR9": {"FROM": "Vancouver (YVR)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "02:00", "STA": "05:25", "Total Time": "13h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR10": {"FROM": "Taipei (TPE)", "To": "Vancouver (YVR)", "AIRCRAFT": "77W", "STD": "23:55", "STA": "19:50", "Total Time": "10h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR117": {"FROM": "Sapporo (CTS)", "To": "Taipei (TPE)", "AIRCRAFT": "A333", "STD": "16:15", "STA": "19:30", "Total Time": "4h 15m", "Days": [1,2,3,4,5,6,7]},
    "BR121": {"FROM": "Okinawa (OKA)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "11:50", "STA": "12:30", "Total Time": "1h 40m", "Days": [1,2,3,4,5,6,7]},
    "BR122": {"FROM": "Taipei (TPE)", "To": "Okinawa (OKA)", "AIRCRAFT": "A321", "STD": "08:15", "STA": "10:45", "Total Time": "1h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR129": {"FROM": "Osaka (KIX)", "To": "Taipei (TPE)", "AIRCRAFT": "781", "STD": "18:30", "STA": "20:30", "Total Time": "3h 00m", "Days": [1,2,3,4,5,6,7]},
    "BR130": {"FROM": "Taipei (TPE)", "To": "Osaka (KIX)", "AIRCRAFT": "781", "STD": "13:35", "STA": "17:15", "Total Time": "2h 40m", "Days": [1,2,3,4,5,6,7]},
    "BR131": {"FROM": "Osaka (KIX)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "13:10", "STA": "15:05", "Total Time": "2h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR132": {"FROM": "Taipei (TPE)", "To": "Osaka (KIX)", "AIRCRAFT": "77W", "STD": "08:20", "STA": "11:55", "Total Time": "2h 35m", "Days": [1,2,3,4,5,6,7]},
    "BR157": {"FROM": "Komatsu (KMQ)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "11:45", "STA": "14:35", "Total Time": "3h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR158": {"FROM": "Taipei (TPE)", "To": "Komatsu (KMQ)", "AIRCRAFT": "A321", "STD": "06:35", "STA": "10:25", "Total Time": "2h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR159": {"FROM": "Seoul (ICN)", "To": "Taipei (TPE)", "AIRCRAFT": "A333", "STD": "19:45", "STA": "21:40", "Total Time": "2h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR160": {"FROM": "Taipei (TPE)", "To": "Seoul (ICN)", "AIRCRAFT": "A333", "STD": "15:15", "STA": "18:45", "Total Time": "2h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR163": {"FROM": "Seoul (ICN)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "20:40", "STA": "22:30", "Total Time": "2h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR164": {"FROM": "Taipei (TPE)", "To": "Seoul (ICN)", "AIRCRAFT": "A321", "STD": "16:30", "STA": "20:00", "Total Time": "2h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR165": {"FROM": "Seoul (ICN)", "To": "Kaohsiung (KHH)", "AIRCRAFT": "A321", "STD": "12:00", "STA": "14:15", "Total Time": "3h 15m", "Days": [1,2,3,4,5,6,7]},
    "BR166": {"FROM": "Kaohsiung (KHH)", "To": "Seoul (ICN)", "AIRCRAFT": "A321", "STD": "07:00", "STA": "10:55", "Total Time": "2h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR169": {"FROM": "Seoul (ICN)", "To": "Taipei (TPE)", "AIRCRAFT": "A333", "STD": "11:40", "STA": "13:30", "Total Time": "2h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR170": {"FROM": "Taipei (TPE)", "To": "Seoul (ICN)", "AIRCRAFT": "A333", "STD": "07:05", "STA": "10:30", "Total Time": "2h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR177": {"FROM": "Osaka (KIX)", "To": "Taipei (TPE)", "AIRCRAFT": "781", "STD": "10:55", "STA": "12:55", "Total Time": "3h 00m", "Days": [1,2,3,4,5,6,7]},
    "BR178": {"FROM": "Taipei (TPE)", "To": "Osaka (KIX)", "AIRCRAFT": "781", "STD": "06:30", "STA": "09:55", "Total Time": "2h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR233": {"FROM": "Taipei (TPE)", "To": "Jakarta (CGK)", "AIRCRAFT": "77W", "STD": "08:45", "STA": "13:10", "Total Time": "5h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR234": {"FROM": "Jakarta (CGK)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "14:30", "STA": "21:00", "Total Time": "5h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR265": {"FROM": "Taipei (TPE)", "To": "Phnom Penh (PNH)", "AIRCRAFT": "A321", "STD": "09:10", "STA": "11:55", "Total Time": "3h 45m", "Days": [1,2,3,4,5,6,7]},
    "BR266": {"FROM": "Phnom Penh (PNH)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "12:55", "STA": "17:15", "Total Time": "3h 20m", "Days": [1,2,3,4,5,6,7]},
    "BR271": {"FROM": "Manila (MNL)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "12:50", "STA": "15:00", "Total Time": "2h 10m", "Days": [1,2,3,4,5,6,7]},
    "BR272": {"FROM": "Taipei (TPE)", "To": "Manila (MNL)", "AIRCRAFT": "77W", "STD": "09:30", "STA": "11:50", "Total Time": "2h 20m", "Days": [1,2,3,4,5,6,7]},
    "BR277": {"FROM": "Manila (MNL)", "To": "Taipei (TPE)", "AIRCRAFT": "787", "STD": "19:00", "STA": "21:30", "Total Time": "2h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR278": {"FROM": "Taipei (TPE)", "To": "Manila (MNL)", "AIRCRAFT": "787", "STD": "15:30", "STA": "17:50", "Total Time": "2h 20m", "Days": [1,2,3,4,5,6,7]},
    "BR383": {"FROM": "Taipei (TPE)", "To": "Da Nang (DAD)", "AIRCRAFT": "A321", "STD": "09:45", "STA": "11:40", "Total Time": "2h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR384": {"FROM": "Da Nang (DAD)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "14:10", "STA": "18:05", "Total Time": "2h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR385": {"FROM": "Taipei (TPE)", "To": "Hanoi (HAN)", "AIRCRAFT": "A321", "STD": "14:50", "STA": "17:15", "Total Time": "3h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR386": {"FROM": "Hanoi (HAN)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "18:30", "STA": "22:20", "Total Time": "2h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR397": {"FROM": "Taipei (TPE)", "To": "Hanoi (HAN)", "AIRCRAFT": "77W", "STD": "09:15", "STA": "11:35", "Total Time": "3h 20m", "Days": [1,2,3,4,5,6,7]},
    "BR398": {"FROM": "Hanoi (HAN)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "12:05", "STA": "15:55", "Total Time": "2h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR721": {"FROM": "Shanghai (PVG)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "20:05", "STA": "22:00", "Total Time": "1h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR722": {"FROM": "Taipei (TPE)", "To": "Shanghai (PVG)", "AIRCRAFT": "77W", "STD": "16:30", "STA": "18:35", "Total Time": "2h 05m", "Days": [1,2,3,4,5,6,7]},
    "BR757": {"FROM": "Hangzhou (HGH)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "19:35", "STA": "21:30", "Total Time": "1h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR758": {"FROM": "Taipei (TPE)", "To": "Hangzhou (HGH)", "AIRCRAFT": "A321", "STD": "16:25", "STA": "18:15", "Total Time": "1h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR765": {"FROM": "Taipei (TPE)", "To": "Chengdu (TFU)", "AIRCRAFT": "A321", "STD": "16:20", "STA": "20:15", "Total Time": "3h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR766": {"FROM": "Chengdu (TFU)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "21:30", "STA": "00:50", "Total Time": "3h 20m", "Days": [1,2,3,4,5,6,7]},
    "BR771": {"FROM": "Shanghai (SHA)", "To": "Taipei (TSA)", "AIRCRAFT": "78X", "STD": "19:40", "STA": "21:45", "Total Time": "2h 05m", "Days": [1,2,3,4,5,6,7]},
    "BR772": {"FROM": "Taipei (TSA)", "To": "Shanghai (SHA)", "AIRCRAFT": "78X", "STD": "14:40", "STA": "16:30", "Total Time": "1h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR805": {"FROM": "Macau (MFM)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "13:15", "STA": "15:00", "Total Time": "1h 45m", "Days": [1,2,3,4,5,6,7]},
    "BR806": {"FROM": "Taipei (TPE)", "To": "Macau (MFM)", "AIRCRAFT": "A321", "STD": "10:45", "STA": "12:35", "Total Time": "1h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR867": {"FROM": "Taipei (TPE)", "To": "Hong Kong (HKG)", "AIRCRAFT": "787", "STD": "10:25", "STA": "12:10", "Total Time": "1h 45m", "Days": [1,2,3,4,5,6,7]},
    "BR868": {"FROM": "Hong Kong (HKG)", "To": "Taipei (TPE)", "AIRCRAFT": "787", "STD": "13:40", "STA": "15:25", "Total Time": "1h 45m", "Days": [1,2,3,4,5,6,7]},
    "BR869": {"FROM": "Taipei (TPE)", "To": "Hong Kong (HKG)", "AIRCRAFT": "787", "STD": "12:25", "STA": "14:15", "Total Time": "1h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR870": {"FROM": "Hong Kong (HKG)", "To": "Taipei (TPE)", "AIRCRAFT": "787", "STD": "15:30", "STA": "17:10", "Total Time": "1h 40m", "Days": [1,2,3,4,5,6,7]},
    "BR891": {"FROM": "Taipei (TPE)", "To": "Hong Kong (HKG)", "AIRCRAFT": "781", "STD": "07:00", "STA": "08:50", "Total Time": "1h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR892": {"FROM": "Hong Kong (HKG)", "To": "Taipei (TPE)", "AIRCRAFT": "781", "STD": "10:10", "STA": "11:55", "Total Time": "1h 45m", "Days": [1,2,3,4,5,6,7]},
    "BR6535": {"FROM": "Taipei (TPE)", "To": "Charter/Cargo", "AIRCRAFT": "N/A", "STD": "N/A", "STA": "N/A", "Total Time": "N/A", "Days": [1,2,3,4,5,6,7]},
    "BR7187": {"FROM": "Taipei (TPE)", "To": "Charter/Cargo", "AIRCRAFT": "N/A", "STD": "N/A", "STA": "N/A", "Total Time": "N/A", "Days": [1,2,3,4,5,6,7]},
    "BR7188": {"FROM": "Charter/Cargo", "To": "Taipei (TPE)", "AIRCRAFT": "N/A", "STD": "N/A", "STA": "N/A", "Total Time": "N/A", "Days": [1,2,3,4,5,6,7]},

    # ==== 長程線與擴充航線 ====
    "BR11": {"FROM": "Taipei (TPE)", "To": "Los Angeles (LAX)", "AIRCRAFT": "77W", "STD": "23:40", "STA": "19:10", "Total Time": "11h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR15": {"FROM": "Taipei (TPE)", "To": "Los Angeles (LAX)", "AIRCRAFT": "77W", "STD": "16:10", "STA": "11:50", "Total Time": "11h 40m", "Days": [1,2,3,4,5,6,7]},
    "BR5": {"FROM": "Taipei (TPE)", "To": "Los Angeles (LAX)", "AIRCRAFT": "77W", "STD": "10:10", "STA": "05:50", "Total Time": "11h 40m", "Days": [1,3,5]},
    "BR32": {"FROM": "Taipei (TPE)", "To": "New York (JFK)", "AIRCRAFT": "77W", "STD": "19:10", "STA": "22:05", "Total Time": "14h 55m", "Days": [1,2,3,4,5,6,7]},
    "BR87": {"FROM": "Taipei (TPE)", "To": "Paris (CDG)", "AIRCRAFT": "77W", "STD": "23:50", "STA": "06:55", "Total Time": "14h 05m", "Days": [1,2,3,4,5,6,7]},
    "BR67": {"FROM": "Taipei (TPE)", "To": "London (LHR)", "AIRCRAFT": "77W", "STD": "09:00", "STA": "19:25", "Total Time": "17h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR75": {"FROM": "Taipei (TPE)", "To": "Amsterdam (AMS)", "AIRCRAFT": "77W", "STD": "08:30", "STA": "19:35", "Total Time": "18h 05m", "Days": [2,4,6]},
    "BR65": {"FROM": "Taipei (TPE)", "To": "Vienna (VIE)", "AIRCRAFT": "787", "STD": "23:30", "STA": "06:35", "Total Time": "14h 05m", "Days": [1,3,5,7]},
    "BR71": {"FROM": "Taipei (TPE)", "To": "Munich (MUC)", "AIRCRAFT": "787", "STD": "23:25", "STA": "07:25", "Total Time": "15h 00m", "Days": [1,3,5,7]},
    "BR95": {"FROM": "Taipei (TPE)", "To": "Milan (MXP)", "AIRCRAFT": "787", "STD": "23:20", "STA": "06:30", "Total Time": "14h 10m", "Days": [2,4,6,7]},
    "BR315": {"FROM": "Taipei (TPE)", "To": "Brisbane (BNE)", "AIRCRAFT": "787", "STD": "09:10", "STA": "20:00", "Total Time": "8h 50m", "Days": [1,2,4,5,6]},
    "BR56": {"FROM": "Taipei (TPE)", "To": "Chicago (ORD)", "AIRCRAFT": "77W", "STD": "20:00", "STA": "20:00", "Total Time": "14h 00m", "Days": [1,3,5,7]},
    "BR26": {"FROM": "Taipei (TPE)", "To": "Seattle (SEA)", "AIRCRAFT": "781", "STD": "23:40", "STA": "18:10", "Total Time": "10h 30m", "Days": [1,2,3,4,5,6,7]},
    "BR8": {"FROM": "Taipei (TPE)", "To": "San Francisco (SFO)", "AIRCRAFT": "77W", "STD": "23:30", "STA": "18:40", "Total Time": "11h 10m", "Days": [1,2,3,4,5,6,7]},
    "BR18": {"FROM": "Taipei (TPE)", "To": "San Francisco (SFO)", "AIRCRAFT": "77W", "STD": "19:50", "STA": "15:00", "Total Time": "11h 10m", "Days": [1,2,3,4,5,6,7]},
    "BR28": {"FROM": "Taipei (TPE)", "To": "San Francisco (SFO)", "AIRCRAFT": "77W", "STD": "23:30", "STA": "18:40", "Total Time": "11h 10m", "Days": [1,2,3,4,5,6,7]},
    "BR36": {"FROM": "Taipei (TPE)", "To": "Toronto (YYZ)", "AIRCRAFT": "77W", "STD": "19:40", "STA": "20:30", "Total Time": "14h 50m", "Days": [1,2,3,4,5,6,7]},
    "BR202": {"FROM": "Taipei (TPE)", "To": "Bangkok (BKK)", "AIRCRAFT": "77W", "STD": "20:45", "STA": "23:30", "Total Time": "3h 45m", "Days": [1,2,3,4,5,6,7]},
    "BR215": {"FROM": "Taipei (TPE)", "To": "Singapore (SIN)", "AIRCRAFT": "77W", "STD": "09:25", "STA": "13:50", "Total Time": "4h 25m", "Days": [1,2,3,4,5,6,7]},
    "BR198": {"FROM": "Taipei (TPE)", "To": "Tokyo (NRT)", "AIRCRAFT": "787", "STD": "08:50", "STA": "13:15", "Total Time": "3h 25m", "Days": [1,2,3,4,5,6,7]},
}

# ==========================================
# 每日自動抓取並更新常態資料庫 (一天僅執行一次)
# ==========================================
@st.cache_data(ttl=86400, show_spinner="🔄 每日例行更新常態航班資料庫 (一天僅執行一次，約需 30-60 秒)...")
def get_daily_updated_db():
    updated_db = {}
    for k, v in MASTER_STATIC_DB.items():
        updated_db[k] = v.copy()

    def fetch_flight_times(flight_no, info):
        fa_flight_id = flight_no.upper().replace("BR", "EVA")
        fa_url = f"https://zh-tw.flightaware.com/live/flight/{fa_flight_id}"
        payload = {
            'api_key': "c84488b98c1d6af5b8b94b306c2e6001",
            'url': fa_url
        }
        try:
            res = requests.get('http://api.scraperapi.com', params=payload, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                scripts = soup.find_all("script")
                for s in scripts:
                    if s.string and "__APOLLO_STATE__" in s.string:
                        match = re.search(r'__APOLLO_STATE__\s*=\s*({.*?});', s.string, re.DOTALL)
                        if match:
                            apollo_data = json.loads(match.group(1))
                            today_str = datetime.now(TW_TZ).strftime("%Y-%m-%d")
                            
                            for key, val in apollo_data.items():
                                if isinstance(val, dict) and "gateDepartureTimes" in val and "gateArrivalTimes" in val:
                                    s_ts = val.get("gateDepartureTimes", {}).get("scheduled") or val.get("takeoffTimes", {}).get("scheduled")
                                    a_ts = val.get("gateArrivalTimes", {}).get("scheduled") or val.get("landingTimes", {}).get("scheduled")
                                    
                                    if s_ts:
                                        # 確保只抓取與今日相關的航班計畫表，防止亂抓到過去的
                                        dt_str = datetime.fromtimestamp(s_ts, TW_TZ).strftime("%Y-%m-%d")
                                        if dt_str == today_str:
                                            info["STD"] = datetime.fromtimestamp(s_ts, TW_TZ).strftime("%H:%M")
                                            if a_ts: 
                                                info["STA"] = datetime.fromtimestamp(a_ts, TW_TZ).strftime("%H:%M")
                                                # 同步更新正確的總飛行時間
                                                if a_ts > s_ts:
                                                    total_mins = int((a_ts - s_ts) / 60)
                                                    h = total_mins // 60
                                                    m = total_mins % 60
                                                    info["Total Time"] = f"{h}h {m}m"
                                            return flight_no, info
        except Exception:
            pass
        return flight_no, info

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_flight = {executor.submit(fetch_flight_times, f, info): f for f, info in updated_db.items()}
        for future in concurrent.futures.as_completed(future_to_flight):
            try:
                f_no, updated_info = future.result()
                updated_db[f_no] = updated_info
            except:
                pass

    return updated_db

# 自動啟用每日更新的常態資料庫
DYNAMIC_MASTER_DB = get_daily_updated_db()

def fetch_single_flight(flight_number):
    flight_upper = flight_number.upper()
    
    if flight_upper in DYNAMIC_MASTER_DB:
        record = DYNAMIC_MASTER_DB[flight_upper]
        return {
            "Flight": flight_upper,
            "FROM": record["FROM"],
            "To": record["To"],
            "AIRCRAFT": record["AIRCRAFT"],
            "STD": record["STD"],
            "STA": record["STA"],
            "Total Time": record["Total Time"],
            "Days": record.get("Days", [1,2,3,4,5,6,7])
        }
    
    return {
        "Flight": flight_upper,
        "FROM": "N/A",
        "To": "N/A",
        "AIRCRAFT": "N/A",
        "STD": "N/A",
        "STA": "N/A",
        "Total Time": "N/A",
        "Days": []
    }

# 輔助函數：格式化總飛行時間
def format_total_time(flight_no, t_time):
    if flight_no == "BR869": return "1小時41分"
    if flight_no == "BR870": return "1小時40分"
    if not t_time or t_time == "N/A": return "無資料"
    return t_time.replace("h ", "小時").replace("m", "分")

@st.cache_data(ttl=1800) 
def get_all_flight_data(flights):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_flight = {executor.submit(fetch_single_flight, f): f for f in flights}
        for future in concurrent.futures.as_completed(future_to_flight):
            flight = future_to_flight[future]
            try:
                results[flight] = future.result()
            except:
                results[flight] = {
                    "Flight": flight.upper(),
                    "FROM": "N/A",
                    "To": "N/A",
                    "AIRCRAFT": "N/A",
                    "STD": "N/A",
                    "STA": "N/A",
                    "Total Time": "N/A"
                }
    return results

def get_live_flight_url(flight):
    flight_upper = flight.upper()
    fa_flight_id = flight_upper.replace("BR", "EVA") if flight_upper.startswith("BR") else flight_upper
    fa_url = f"https://www.flightaware.com/live/flight/{fa_flight_id}"
    return fa_url

@st.cache_data(ttl=60) 
def get_all_flight_urls(flights):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_flight = {executor.submit(get_live_flight_url, f): f for f in flights}
        for future in concurrent.futures.as_completed(future_to_flight):
            flight = future_to_flight[future]
            try:
                results[flight] = future.result()
            except:
                fa_id = flight.upper().replace("BR", "EVA") if flight.upper().startswith("BR") else flight.upper()
                results[flight] = f"https://www.flightaware.com/live/flight/{fa_id}"
    return results

# ==========================================
# 共享資料管理 (Session State)
# ==========================================

if 'family_data' not in st.session_state:
    st.session_state.family_data = [
        {"name": "孟竹", "birth_date": date(1988, 10, 31), "category": "孟竹家"},
        {"name": "衣宸", "birth_date": date(1993, 6, 7), "category": "孟竹家"},
        {"name": "沁玹", "birth_date": date(2022, 4, 12), "category": "孟竹家"},
        {"name": "承豐", "birth_date": date(2023, 10, 17), "category": "孟竹家"},
        {"name": "清標", "birth_date": date(1955, 10, 25), "category": "標仔家"},
        {"name": "蓮瑞", "birth_date": date(1959, 4, 8), "category": "標仔家"},
        {"name": "子瑩", "birth_date": date(1985, 3, 29), "category": "標仔家"},
        {"name": "子欣", "birth_date": date(1987, 4, 4), "category": "標仔家"},
    ]

if 'selected_flight' not in st.session_state:
    st.session_state.selected_flight = None

FAMILY_GROUPS = ["孟竹家", "標仔家", "其他"]

with st.sidebar:
    st.header("➕ 新增家庭成員")
    new_name = st.text_input("姓名")
    new_date = st.date_input("國曆生日", min_value=date(1900, 1, 1))
    new_category = st.selectbox("歸屬家族", FAMILY_GROUPS, index=2) 
    
    if st.button("加入名單"):
        if new_name:
            st.session_state.family_data.append({
                "name": new_name,
                "birth_date": new_date,
                "category": new_category
            })
            st.success(f"已加入 {new_name} 到 {new_category}！")
        else:
            st.error("請輸入姓名")
            
    st.divider()
    if st.button("重置/清空名單"):
        st.session_state.family_data = []
        st.rerun()

st.markdown('<div class="main-title">宸竹專屬工具箱app</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✈️ 衣宸航班", "🛠️ 日常工具 & 路況", "🎂 家族生日 & 時光"])

# ------------------------------------------------------------------
# TAB 1: 衣宸航班
# ------------------------------------------------------------------
with tab1:
    
    st.markdown("### 📋 上傳本月班表")
    uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    SCHEDULE_FILE = "shared_schedule.png"

    if uploaded_file is not None:
        with open(SCHEDULE_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ 班表已成功上傳！現在別人打開網址也會看到這張圖表。")

        if Image is not None and pytesseract is not None:
            try:
                img = Image.open(SCHEDULE_FILE)
                text = pytesseract.image_to_string(img, config='--psm 6')
                
                # 自動抓取資料：建立或更新動態班表 JSON
                dynamic_schedule = {}
                if os.path.exists("dynamic_schedule.json"):
                    try:
                        with open("dynamic_schedule.json", "r", encoding="utf-8") as f:
                            dynamic_schedule = json.load(f)
                    except:
                        pass
                
                # 嘗試解析月份和年份 (例如 "Mar 2026")
                today_tw = datetime.now(TW_TZ)
                year = today_tw.year
                month = today_tw.month
                my_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', text, re.IGNORECASE)
                if my_match:
                    month_str = my_match.group(1)[:3].capitalize()
                    year = int(my_match.group(2))
                    month_map = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                    month = month_map.get(month_str, month)
                
                words = text.split()
                new_flights = []
                
                # 簡單的正則掃描：找出可能是日期的數字，接著是航班代碼
                for i in range(len(words) - 3):
                    if words[i].isdigit() and 1 <= int(words[i]) <= 31:
                        day = int(words[i])
                        # 如果下個字是 2~4 位數字 (班機號)
                        if words[i+1].isdigit() and 2 <= len(words[i+1]) <= 4:
                            f1 = "BR" + words[i+1]
                            f2 = None
                            aircraft = "N/A"
                            
                            if words[i+2].isdigit() and 2 <= len(words[i+2]) <= 4:
                                f2 = "BR" + words[i+2]
                                if re.match(r'(A3|B7)[A-Z0-9]{2,3}', words[i+3], re.IGNORECASE):
                                    aircraft = words[i+3].upper()
                            elif re.match(r'(A3|B7)[A-Z0-9]{2,3}', words[i+2], re.IGNORECASE):
                                aircraft = words[i+2].upper()
                            
                            date_key = f"{year}-{month:02d}-{day:02d}"
                            flights_list = [f1]
                            if f2: flights_list.append(f2)
                            
                            dynamic_schedule[date_key] = {"flights": flights_list, "aircraft": aircraft}
                            new_flights.extend(flights_list)
                
                if dynamic_schedule:
                    with open("dynamic_schedule.json", "w", encoding="utf-8") as f:
                        json.dump(dynamic_schedule, f)
                    st.success("🔍 自動從班表中成功擷取並更新了每日服勤資料！")

                found_flights = re.findall(r'BR\d{1,4}', text, re.IGNORECASE) + new_flights
                if found_flights:
                    found_flights = [f.upper() for f in found_flights]
                    saved_list = []
                    if os.path.exists("known_flights.json"):
                        with open("known_flights.json", "r", encoding="utf-8") as jf:
                            saved_list = json.load(jf)
                            
                    new_added = [f for f in set(found_flights) if f not in saved_list]
                    if new_added:
                        saved_list.extend(new_added)
                        with open("known_flights.json", "w", encoding="utf-8") as jf:
                            json.dump(saved_list, jf)
            except Exception as e:
                pass
                
    if os.path.exists(SCHEDULE_FILE):
        st.image(SCHEDULE_FILE, use_column_width=True)
    else:
        st.markdown("""
            <div style="background-color: #4a90e2; height: 500px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; border-radius: 5px; font-size: 20px;">
                尚無圖片，請由上方上傳班表
            </div>
        """, unsafe_allow_html=True)
        
    st.divider()

    st.markdown("""
        <style>
        .flight-btn-red {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #ea4335; 
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 4px;
            text-decoration: none !important;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: opacity 0.3s, transform 0.2s;
            min-width: 80px;
        }
        .flight-btn-red:hover {
            opacity: 0.85;
            transform: translateY(-2px);
        }
        
        .flight-btn-today {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #003366; 
            color: #ffffff !important; 
            padding: 6px 14px;
            border-radius: 4px;
            text-decoration: none !important;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: opacity 0.3s, transform 0.2s;
            min-width: 80px;
            border: 2px solid #001a33; 
        }
        .flight-btn-today:hover {
            opacity: 0.85;
            transform: translateY(-2px);
        }
        
        .flight-btn-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    SCHEDULE_STATIC = {
        date(2026, 3, 2): {"flights": ["BR178", "BR177"], "aircraft": "B78N"},
        date(2026, 3, 3): {"flights": ["BR265", "BR266"], "aircraft": "A333"},
        date(2026, 3, 4): {"flights": ["BR160", "BR159"], "aircraft": "B78P"},
        date(2026, 3, 6): {"flights": ["BR397", "BR398"], "aircraft": "B77A"},
        date(2026, 3, 8): {"flights": ["BR891", "BR892"], "aircraft": "B781"},
        date(2026, 3, 9): {"flights": ["BR170", "BR169"], "aircraft": "A333"},
        date(2026, 3, 12): {"flights": ["BR7187", "BR7188"], "aircraft": "B78P"},
        date(2026, 3, 13): {"flights": ["BR160", "BR159"], "aircraft": "B78P"},
        date(2026, 3, 15): {"flights": ["BR178", "BR177"], "aircraft": "B78N"},
        date(2026, 3, 18): {"flights": ["BR10"], "aircraft": "B77B"},
        date(2026, 3, 20): {"flights": ["BR9"], "aircraft": "B77B"},
        date(2026, 3, 21): {"flights": ["BR9"], "aircraft": "B77B"},
        date(2026, 3, 29): {"flights": ["BR166", "BR165"], "aircraft": "A321"},
        date(2026, 3, 30): {"flights": ["BR130", "BR129"], "aircraft": "B781"},
        date(2026, 3, 31): {"flights": ["BR277", "BR278"], "aircraft": "A333"},
    }

    current_schedule = SCHEDULE_STATIC.copy()
    if os.path.exists("dynamic_schedule.json"):
        try:
            with open("dynamic_schedule.json", "r", encoding="utf-8") as f:
                raw_dyn = json.load(f)
                for k, v in raw_dyn.items():
                    try:
                        dt = datetime.strptime(k, "%Y-%m-%d").date()
                        current_schedule[dt] = v
                    except:
                        pass
        except:
            pass

    base_flights = [
        "BR178", "BR177", "BR265", "BR266", "BR160", "BR159", "BR397", "BR398", "BR6535",
        "BR869", "BR870", "BR867", "BR868", "BR805", "BR806", "BR758", "BR757", 
        "BR10", "BR9", "BR166", "BR165", "BR130", "BR129", "BR277", "BR278",
        "BR169", "BR170", "BR271", "BR272", "BR891", "BR892", "BR132", "BR131", 
        "BR383", "BR384", "BR772", "BR771", "BR117", "BR385", "BR386", "BR158", 
        "BR157", "BR233", "BR234",
        "BR722", "BR721", "BR765", "BR766", "BR122", "BR121", "BR164", "BR163",
        "BR7187", "BR7188"
    ]
    
    saved_flights = []
    if os.path.exists("known_flights.json"):
        try:
            with open("known_flights.json", "r", encoding="utf-8") as f:
                saved_flights = json.load(f)
        except:
            pass
            
    schedule_flights = []
    for d, info in current_schedule.items():
        schedule_flights.extend(info["flights"])
        
    all_unique_flights = list(set(base_flights + saved_flights + schedule_flights))
    
    with open("known_flights.json", "w", encoding="utf-8") as f:
        json.dump(all_unique_flights, f)

    flights = all_unique_flights
    flights = sorted(flights, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf'))
    
    with st.spinner("🚀 正在即時抓取最新航班資訊與動態路徑，請稍候..."):
        all_flight_data = get_all_flight_data(flights)
        all_flight_urls = get_all_flight_urls(flights)
    
    today_date = datetime.now(TW_TZ).date()
    today_data = current_schedule.get(today_date, {"flights": [], "aircraft": ""})
    today_flights = today_data.get("flights", [])
    today_aircraft = today_data.get("aircraft", "N/A")

    df_report_raw = pd.DataFrame([all_flight_data[f] for f in flights])
    
    schedule_aircraft_map = {}
    for d, info in current_schedule.items():
        for f in info["flights"]:
            schedule_aircraft_map[f] = info["aircraft"]
    for f in today_flights:
        schedule_aircraft_map[f] = today_aircraft
        
    df_report_raw['AIRCRAFT'] = df_report_raw.apply(
        lambda row: schedule_aircraft_map[row['Flight']] if row['Flight'] in schedule_aircraft_map else row['AIRCRAFT'], 
        axis=1
    )
    df_report_raw = df_report_raw[["Flight", "FROM", "To", "AIRCRAFT", "STD", "STA", "Total Time"]]
    
    df_today = df_report_raw[df_report_raw["Flight"].isin(today_flights)]
    df_other = df_report_raw[~df_report_raw["Flight"].isin(today_flights)]
    df_report_ordered = pd.concat([df_today, df_other], ignore_index=True)

    selected_flight_from_table = None
    if "flight_table_selection" in st.session_state:
        sel_dict = st.session_state.flight_table_selection
        if "selection" in sel_dict and "rows" in sel_dict["selection"]:
            sel_rows = sel_dict["selection"]["rows"]
            if sel_rows:
                selected_idx = sel_rows[0]
                selected_flight_from_table = df_report_ordered.iloc[selected_idx]["Flight"]

    st.markdown("### ℹ️ 今日服勤航班資訊欄")
    
    if not today_flights and not selected_flight_from_table:
        st.info("今日無安排服勤航班，休假愉快！")
    else:
        outbound_flight = None
        return_flight = None
        disp_aircraft = today_aircraft
        
        if selected_flight_from_table:
            rec = fetch_single_flight(selected_flight_from_table)
            try:
                disp_aircraft = df_report_ordered[df_report_ordered["Flight"] == selected_flight_from_table]["AIRCRAFT"].values[0]
            except:
                disp_aircraft = "N/A"
            if any(x in rec.get("To", "") for x in ["Taipei", "TPE", "TSA", "Kaohsiung", "KHH"]):
                return_flight = rec
            else:
                outbound_flight = rec
        else:
            for f in today_flights:
                rec = fetch_single_flight(f)
                if any(x in rec.get("FROM", "") for x in ["Taipei", "TPE", "TSA", "Kaohsiung", "KHH"]):
                    outbound_flight = rec
                elif any(x in rec.get("To", "") for x in ["Taipei", "TPE", "TSA", "Kaohsiung", "KHH"]):
                    return_flight = rec
                    
            if not outbound_flight and len(today_flights) > 0:
                outbound_flight = fetch_single_flight(today_flights[0])
            if not return_flight and len(today_flights) > 1:
                return_flight = fetch_single_flight(today_flights[1])
                
        def extract_airport_code(s):
            m = re.search(r'\((.*?)\)', s)
            return m.group(1) if m else s
            
        out_airport = "N/A"
        ret_airport = "N/A"
        dest_city = "目的地"
        out_code = ""
        ret_code = ""
        
        if outbound_flight and outbound_flight.get("Flight") != "N/A":
            out_code = extract_airport_code(outbound_flight.get("FROM", ""))
            code_to = extract_airport_code(outbound_flight.get("To", ""))
            out_airport_origin = TERMINAL_INFO.get(out_code, outbound_flight.get("FROM", ""))
            out_airport_dest = TERMINAL_INFO.get(code_to, outbound_flight.get("To", ""))
            out_airport = f"{out_airport_origin} ➔ {out_airport_dest}"
            dest_city = out_airport_dest.split(" ")[0]
            
        if return_flight and return_flight.get("Flight") != "N/A":
            ret_code = extract_airport_code(return_flight.get("FROM", ""))
            ret_to_code = extract_airport_code(return_flight.get("To", ""))
            ret_airport_origin = TERMINAL_INFO.get(ret_code, return_flight.get("FROM", ""))
            ret_airport_dest = TERMINAL_INFO.get(ret_to_code, return_flight.get("To", ""))
            ret_airport = f"{ret_airport_origin} ➔ {ret_airport_dest}"
            if dest_city == "目的地":
                dest_city = ret_airport_origin.split(" ")[0]

        st.markdown('<div class="info-panel-card">', unsafe_allow_html=True)
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            if outbound_flight and outbound_flight.get("Flight") != "N/A":
                fa_url_out = get_live_flight_url(outbound_flight['Flight'])
                
                st.markdown(f'<div class="info-text-large"><span class="info-label">🛫 去程航班:</span> {outbound_flight["Flight"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text-normal"><span class="info-label">✈️ 機型:</span> {disp_aircraft}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text-normal"><span class="info-label">🏢 出發機場與航廈:</span> {out_airport}</div>', unsafe_allow_html=True)
                
                out_weather = get_airport_weather(out_code) if out_code else "暫無資料"
                st.markdown(f'''
                    <div class="weather-premium-card">
                        <div class="weather-premium-title">🌤️ 出發地天氣</div>
                        <div class="weather-premium-data">{out_weather}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                std_time = outbound_flight["STD"]
                sched_dep_str, gate_dep_str, delay_mins, sched_takeoff_str, takeoff_str, taxi_mins, eta_str = get_realtime_flight_status(outbound_flight["Flight"], std_time)
                
                sched_dep_str_html = f"<span style='color:#333333;'>{sched_dep_str}</span>"
                if any(x in str(sched_dep_str) for x in ["無資料", "無法計算"]): sched_dep_str_html = f"<span style='color:#757575;'>{sched_dep_str}</span>"

                flight_time_str_out = format_total_time(outbound_flight["Flight"], outbound_flight.get("Total Time", ""))

                st.markdown(f'''
                    <div class="time-premium-box">
                        <div class="time-row"><span class="time-label">⏱️ 計畫出發時間 (STD):</span> <span class="time-value">{sched_dep_str_html}</span></div>
                        <div class="time-row"><span class="time-label">🛬 計畫抵達時間 (STA):</span> <span class="time-value"><span style='color:#333333;'>{outbound_flight["STA"]}</span></span></div>
                        <div class="time-row" style="border-bottom:none;"><span class="time-label">⏱️ 總飛行時間:</span> <span class="time-value"><span style='color:#1565C0;'>{flight_time_str_out}</span></span></div>
                        <div style="margin-top: 12px; text-align: right;">
                            <a href="{fa_url_out}" target="_blank" class="live-link-btn" style="background-color: #E65100; font-size: 22px; padding: 12px 20px; border-radius: 8px;">✈️ 航班雷達動態</a>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-text-large">無去程航班資訊</div>', unsafe_allow_html=True)
                
        with col_info2:
            if return_flight and return_flight.get("Flight") != "N/A":
                fa_url_ret = get_live_flight_url(return_flight['Flight'])
                
                st.markdown(f'<div class="info-text-large"><span class="info-label">🛬 回程航班:</span> {return_flight["Flight"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text-normal"><span class="info-label">✈️ 機型:</span> {disp_aircraft}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text-normal"><span class="info-label">🏢 回程機場與航廈:</span> {ret_airport}</div>', unsafe_allow_html=True)
                
                ret_weather = get_airport_weather(ret_code) if ret_code else "暫無資料"
                st.markdown(f'''
                    <div class="weather-premium-card">
                        <div class="weather-premium-title">🌤️ 外站出發天氣</div>
                        <div class="weather-premium-data">{ret_weather}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                std_time_ret = return_flight["STD"]
                sched_dep_str_ret, gate_dep_str_ret, delay_mins_ret, sched_takeoff_str_ret, takeoff_str_ret, taxi_mins_ret, eta_str_ret = get_realtime_flight_status(return_flight["Flight"], std_time_ret)
                
                sched_dep_str_html_ret = f"<span style='color:#333333;'>{sched_dep_str_ret}</span>"
                if any(x in str(sched_dep_str_ret) for x in ["無資料", "無法計算"]): sched_dep_str_html_ret = f"<span style='color:#757575;'>{sched_dep_str_ret}</span>"

                flight_time_str_ret = format_total_time(return_flight["Flight"], return_flight.get("Total Time", ""))

                st.markdown(f'''
                    <div class="time-premium-box">
                        <div class="time-row"><span class="time-label">⏱️ 計畫出發時間 (STD):</span> <span class="time-value">{sched_dep_str_html_ret}</span></div>
                        <div class="time-row"><span class="time-label">🛬 計畫抵達時間 (STA):</span> <span class="time-value"><span style='color:#333333;'>{return_flight["STA"]}</span></span></div>
                        <div class="time-row" style="border-bottom:none;"><span class="time-label">⏱️ 總飛行時間:</span> <span class="time-value"><span style='color:#1565C0;'>{flight_time_str_ret}</span></span></div>
                        <div style="margin-top: 12px; text-align: right;">
                            <a href="{fa_url_ret}" target="_blank" class="live-link-btn" style="background-color: #E65100; font-size: 22px; padding: 12px 20px; border-radius: 8px;">✈️ 航班雷達動態</a>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-text-large">無回程航班資訊</div>', unsafe_allow_html=True)
                
        news_items = get_airport_news(dest_city)
        if news_items:
            st.markdown(f"---")
            st.markdown(f"<div class='info-text-large'>📰 『{dest_city}』 當日出差地相關新聞:</div>", unsafe_allow_html=True)
            for idx, n in enumerate(news_items):
                st.markdown(f"<div style='font-size: 18px; margin-bottom: 5px;'>{idx+1}. <a href='{n['link']}' target='_blank' style='color: #0277bd; font-weight: bold;'>{n['title']}</a></div>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("### 🔘 航班快捷按鈕 & 報表")

    col_btns, col_table = st.columns([1, 2], gap="medium")

    with col_btns:
        btn_html = '<div class="flight-btn-container">'
        
        for flight in flights:
            fa_id = flight.upper().replace("BR", "EVA") if flight.upper().startswith("BR") else flight.upper()
            url = all_flight_urls.get(flight, f"https://www.flightaware.com/live/flight/{fa_id}")
            
            if flight.upper() in today_flights:
                btn_class = "flight-btn-today"
            else:
                btn_class = "flight-btn-red"
                
            btn_html += f'<a href="{url}" target="_blank" class="{btn_class}">{flight.upper()}</a>'
        btn_html += '</div>'
        
        st.markdown(btn_html, unsafe_allow_html=True)

    with col_table:
        def highlight_today_flights(row):
            if row['Flight'] in today_flights:
                return ['background-color: #FFF9C4; color: #D32F2F; font-weight: bold;'] * len(row)
            if selected_flight_from_table and row['Flight'] == selected_flight_from_table:
                return ['background-color: #E3F2FD; color: #1565C0; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        styled_report = df_report_ordered.style.apply(highlight_today_flights, axis=1)

        try:
            st.dataframe(
                styled_report, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",            
                selection_mode="single-row", 
                key="flight_table_selection" 
            )
        except Exception:
            st.dataframe(styled_report, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown('<div class="section-title">📅 未來 30 天的長榮航空航班 (桃園起飛)</div>', unsafe_allow_html=True)
    
    @st.cache_data(ttl=3600)
    def get_30_days_tpe_eva_flights():
        today_dt = datetime.now(TW_TZ).date()
        future_data = []
        
        for i in range(30):
            current_date = today_dt + timedelta(days=i)
            current_weekday = current_date.isoweekday() 
            d_str = current_date.strftime("%Y/%m/%d")
            
            daily_flights = []
            
            for flight_no, f_info in DYNAMIC_MASTER_DB.items():
                if "TPE" in f_info["FROM"] or "Taipei" in f_info["FROM"]:
                    if current_weekday in f_info.get("Days", [1,2,3,4,5,6,7]):
                        std_str = f_info["STD"]
                        if len(std_str) == 4 and ":" in std_str:
                            std_str = "0" + std_str
                            
                        daily_flights.append({
                            "1. 日期": d_str,
                            "2. Flight (航班代碼)": flight_no,
                            "3. From (桃園機場起飛)": f_info["FROM"],
                            "4. To (目的地的機場)": f_info["To"],
                            "5. AIRCRAFT (機型)": f_info["AIRCRAFT"],
                            "6. STD (預計起飛時間)": std_str,
                            "7. STA (預計抵達時間)": f_info["STA"],
                            "8. Total Time (總飛行時間)": f_info["Total Time"]
                        })
            
            def time_to_mins(t_str):
                try:
                    parts = t_str.split(":")
                    return int(parts[0]) * 60 + int(parts[1])
                except:
                    return 9999
                    
            daily_flights = sorted(daily_flights, key=lambda x: time_to_mins(x["6. STD (預計起飛時間)"]))
            future_data.extend(daily_flights)
            
        return pd.DataFrame(future_data)

    df_30_days = get_30_days_tpe_eva_flights()
    
    if not df_30_days.empty:
        st.dataframe(df_30_days, use_container_width=True, hide_index=True)
    else:
        st.info("目前無桃園起飛的長榮航班資料。")


# ------------------------------------------------------------------
# TAB 2: 日常工具 & 路況
# ------------------------------------------------------------------
with tab2:
    if st.button("🔄 點擊手動更新所有即時資訊 (路況/天氣)", use_container_width=True, key="refresh_tab1"):
        st.cache_data.clear()
        st.rerun()

    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown('<div class="section-title">即時氣溫 & 降雨率</div>', unsafe_allow_html=True)
        weather_html = get_weather_data_html()
        st.markdown(f"""
        <div class="data-box text-cyan">
            {weather_html}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">🚌 公車動態</div>', unsafe_allow_html=True)
        bus_col1, bus_col2 = st.columns(2)
        with bus_col1:
            st.link_button("🚌 310", "https://ebus.gov.taipei/EBus/VsSimpleMap?routeid=0100031000&gb=1", use_container_width=True)
        with bus_col2:
            st.link_button("🚌 952", "https://ebus.gov.taipei/EBus/VsSimpleMap?routeid=0400095200&gb=0", use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">即時路況 & 大眾運輸</div>', unsafe_allow_html=True)
        st.markdown('<span style="color:#333; font-size:18px;">※ 點擊下方路況文字可直接開啟 Google 地圖</span>', unsafe_allow_html=True)
        
        base_addr = "新北市板橋區民治街61巷33號"
        
        gmaps_client = None
        if GOOGLE_MAPS_API_KEY and "YOUR_KEY" not in GOOGLE_MAPS_API_KEY:
            try:
                gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            except:
                pass
        
        st.markdown('<div class="traffic-section-header">🚇 捷運</div>', unsafe_allow_html=True)
        mrt_target = "捷運中山站"
        txt_go_mrt, cls_go_mrt, url_go_mrt = calculate_traffic(gmaps_client, base_addr, mrt_target, 25, "往中山捷運站", mode='transit')
        txt_back_mrt, cls_back_mrt, url_back_mrt = calculate_traffic(gmaps_client, mrt_target, base_addr, 32, "反江子翠捷運站", mode='transit')
        
        st.markdown(f"""
        <div class="traffic-card">
            <div class="traffic-card-title">中山捷運站 <span style="font-size:16px;">(藍線 > 轉西門綠線 > 中山)</span></div>
            <a href="{url_go_mrt}" target="_blank" class="traffic-row {cls_go_mrt}">{txt_go_mrt}</a>
            <a href="{url_back_mrt}" target="_blank" class="traffic-row {cls_back_mrt}">{txt_back_mrt}</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="traffic-section-header">🛵 騎車</div>', unsafe_allow_html=True)
        target_locations_bike = [
            ("京樺牛肉麵", "臺北市中山區林森北路259巷9-3號", "反板橋", 15, 15)
        ]
        for name, target_addr, return_label, std_go, std_back in target_locations_bike:
            _, cls_go, url_go = calculate_traffic(gmaps_client, base_addr, target_addr, std_go, "往京樺", mode='two_wheeler')
            _, cls_back, url_back = calculate_traffic(gmaps_client, target_addr, base_addr, std_back, return_label, mode='two_wheeler')
            
            url_go += "&waypoints=" + urllib.parse.quote("台北市民生西路")
            txt_go = "往京樺: 15分 (+0分) 7.9km"
            txt_back = "反板橋: 15分 (+0分) 7.3km"

            st.markdown(f"""
            <div class="traffic-card">
                <div class="traffic-card-title">{name} <span style="font-size:16px;">(途經機慢車專用道和民生西路)</span></div>
                <a href="{url_go}" target="_blank" class="traffic-row {cls_go}">{txt_go}</a>
                <a href="{url_back}" target="_blank" class="traffic-row {cls_back}">{txt_back}</a>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="traffic-section-header">🚗 開車</div>', unsafe_allow_html=True)
        target_locations_car = [
            ("板橋家", "新竹市東區太原路128號", "往新竹", "反板橋", 53, 61),
            ("長榮航空", "桃園縣蘆竹鄉新南路一段376號", "往南崁", "反板橋", 22, 27)
        ]
        for name, target_addr, label_go, label_back, std_go, std_back in target_locations_car:
            txt_go, cls_go, url_go = calculate_traffic(gmaps_client, base_addr, target_addr, std_go, label_go, mode='driving')
            txt_back, cls_back, url_back = calculate_traffic(gmaps_client, target_addr, base_addr, std_back, label_back, mode='driving')
            
            st.markdown(f"""
            <div class="traffic-card">
                <div class="traffic-card-title">{name}</div>
                <a href="{url_go}" target="_blank" class="traffic-row {cls_go}">{txt_go}</a>
                <a href="{url_back}" target="_blank" class="traffic-row {cls_back}">{txt_back}</a>
            </div>
            """, unsafe_allow_html=True)
            
    st.divider()
    col_f1, col_f2 = st.columns([1, 4])
    with col_f1:
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #e74c3c;
                color: white;
                font-size: 18px;
            }
            </style>
        """, unsafe_allow_html=True)
        st.link_button("YouTube 轉 MP3", "https://yt1s.ai/zh-tw/youtube-to-mp3/", use_container_width=True)

    with col_f2:
        st.markdown('<div style="margin-top: 10px; color: #555; font-size: 18px;">← 點擊左側按鈕開啟轉檔</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# TAB 3: 家族時光
# ------------------------------------------------------------------
with tab3:
    st.caption(f"<span style='font-size: 18px;'>今天是 {datetime.now(TW_TZ).date().strftime('%Y年%m月%d日')}</span>", unsafe_allow_html=True)

    if not st.session_state.family_data:
        st.info("目前沒有資料，請從左側新增成員。")
    else:
        processed_data = []
        for person in st.session_state.family_data:
            b_date = person['birth_date']
            years, total_days = calculate_detailed_age(b_date)
            zodiac_animal = get_chinese_zodiac(b_date.year)
            zodiac_sign = get_western_zodiac(b_date.day, b_date.month)
            lunar_str = get_lunar_date_str(b_date)
            days_to_next = get_next_birthday_days(b_date)
            days_to_next_lunar = get_next_lunar_birthday_days(b_date) 
            
            category = person.get('category', '未分類')

            processed_data.append({
                "姓名": person['name'],
                "家族": category,
                "國曆生日": b_date.strftime("%Y/%m/%d"),
                "農曆": lunar_str,
                "修正農曆": "", 
                "生肖": zodiac_animal,
                "星座": zodiac_sign,
                "歲數": years,
                "總天數": total_days,
                "距離下次生日(天)": days_to_next,
                "距離下次農曆生日(天)": days_to_next_lunar,
                "詳細年齡字串": f"{years} 歲 又 {total_days % 365} 天"
            })

        df = pd.DataFrame(processed_data)
        
        df_birthday_sorted = df.sort_values(by="距離下次生日(天)")
        
        upcoming = df_birthday_sorted.iloc[0]
        
        b_date_obj_upcoming = datetime.strptime(upcoming['國曆生日'], "%Y/%m/%d").date()
        days_mod_upcoming = (datetime.now(TW_TZ).date() - b_date_obj_upcoming).days % 365
        
        top_col1, top_col2 = st.columns([2, 1])
        
        with top_col1:
            st.markdown('<div class="section-title">🎉 最近的國曆壽星</div>', unsafe_allow_html=True)
            html_card_upcoming = f"""
            <div class="birthday-card top-card-highlight">
                <div class="big-font">
                    {upcoming['姓名']} 
                    <span style="font-size:18px; background-color:#eee; padding:4px 8px; border-radius:4px; margin-left:5px;">{upcoming['家族']}</span>
                    <span style="font-size:16px; color:gray">({upcoming['生肖']})</span>
                </div>
                <hr style="margin: 8px 0;">
                <div class="sub-font">🎂 國曆: {upcoming['國曆生日']}</div>
                <div class="sub-font">🌑 農曆: {upcoming['農曆']}   📝 修正農曆: {upcoming['修正農曆']}</div>
                <div class="sub-font">✨ 星座: {upcoming['星座']}</div>
                <div style="margin-top: 10px;">
                    <span class="highlight">{upcoming['歲數']} 歲</span> 
                    <span style="font-size: 16px; color: #555;">又 {days_mod_upcoming} 天</span>
                </div>
                <div style="margin-top: 10px; font-size: 18px; color: #ff4b4b; font-weight: bold;">
                    ⏳ 距離國曆生日還有: {upcoming['距離下次生日(天)']} 天<br>
                    ⏳ 距離農曆生日還有: {upcoming['距離下次農曆生日(天)']} 天
                </div>
            </div>
            """
            st.markdown(html_card_upcoming, unsafe_allow_html=True)
            
        with top_col2:
            st.write("") 
            st.write("")
            st.metric("👨‍👩‍👧‍👦 家庭成員數", f"{len(df)} 人")

        st.divider()

        st.markdown('<div class="section-title">📋 生日倒數 (下個國曆生日是誰)</div>', unsafe_allow_html=True)
        st.dataframe(
            df_birthday_sorted[["姓名", "家族", "國曆生日", "農曆", "修正農曆", "生肖", "星座", "詳細年齡字串", "距離下次生日(天)", "距離下次農曆生日(天)"]],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.markdown('<div class="section-title">🧓 家族長幼序 (依年齡排序：由上到下)</div>', unsafe_allow_html=True)
        
        df_age_sorted = df.sort_values(by="總天數", ascending=False).reset_index(drop=True)
        sort_order = df_age_sorted['姓名'].tolist()
        
        chart_rendered = False
        
        if alt:
            try:
                domain_colors = ["孟竹家", "標仔家", "其他"]
                range_colors = ["#5DADE2", "#F39C12", "#95A5A6"]

                base = alt.Chart(df_age_sorted).encode(
                    y=alt.Y('姓名:N', sort=sort_order, title=None, axis=alt.Axis(labelFontSize=18, labelFontWeight='bold', labelOverlap=False)), 
                    x=alt.X('歲數:Q', title='年齡 (歲)', axis=alt.Axis(grid=False, labelFontSize=16, titleFontSize=18)), 
                    tooltip=['姓名', '家族', '歲數', '生肖', '國曆生日']
                )

                bars = base.mark_bar(
                    cornerRadiusTopRight=5, 
                    cornerRadiusBottomRight=5,
                    height=30
                ).encode(
                    color=alt.Color('家族:N', 
                                    scale=alt.Scale(domain=domain_colors, range=range_colors), 
                                    legend=alt.Legend(title="家族分類", orient='top', labelFontSize=16, titleFontSize=18))
                )

                text = base.mark_text(
                    align='left',
                    baseline='middle',
                    dx=8,
                    fontSize=18,
                    fontWeight='bold',
                    color='#000000'
                ).encode(
                    text=alt.Text('歲數:Q', format='.0f')
                )
                
                final_chart = (bars + text).properties(
                    title="家族成員年齡分佈",
                    height=len(df_age_sorted) * 55 
                ).configure(
                    background='#ffffff'
                ).configure_title(
                    color='#000000',
                    fontSize=22
                ).configure_axis(
                    labelColor='#000000',
                    titleColor='#000000' 
                ).configure_legend(
                    labelColor='#000000',
                    titleColor='#000000'
                )
                
                st.altair_chart(final_chart, use_container_width=True)
                chart_rendered = True

            except Exception as e:
                st.warning(f"圖表繪製發生錯誤: {e}")
                pass
        else:
             st.warning("未安裝 altair 套件，無法顯示圖表。")

        if not chart_rendered:
            try:
                st.bar_chart(df_age_sorted, x="歲數", y="姓名", color="家族")
            except:
                 st.dataframe(df_age_sorted[["姓名", "家族", "歲數"]])

        st.divider()

        st.markdown('<div class="section-title">📇 詳細資料卡片 (家族分類)</div>', unsafe_allow_html=True)
        
        available_groups = ["全部"] + sorted(list(set(df['家族'].unique())), key=lambda x: FAMILY_GROUPS.index(x) if x in FAMILY_GROUPS else 99)
        
        tabs_family = st.tabs(available_groups)
        
        for i, group_name in enumerate(available_groups):
            with tabs_family[i]:
                if group_name == "全部":
                    current_df = df_birthday_sorted
                else:
                    current_df = df_birthday_sorted[df_birthday_sorted['家族'] == group_name]
                
                if current_df.empty:
                    st.write("此分類尚無成員。")
                else:
                    cols = st.columns(3)
                    for idx, row in current_df.iterrows():
                        loc_idx = current_df.index.get_loc(idx)
                        
                        with cols[loc_idx % 3]:
                            b_date_obj_row = datetime.strptime(row['國曆生日'], "%Y/%m/%d").date()
                            days_mod_row = (datetime.now(TW_TZ).date() - b_date_obj_row).days % 365

                            html_card = f"""
                            <div class="birthday-card">
                                <div class="big-font">
                                    {row['姓名']} 
                                    <span style="font-size:18px; background-color:#eee; padding:4px 8px; border-radius:4px; margin-left:5px;">{row['家族']}</span>
                                    <span style="font-size:16px; color:gray">({row['生肖']})</span>
                                </div>
                                <hr style="margin: 8px 0;">
                                <div class="sub-font">🎂 國曆: {row['國曆生日']}</div>
                                <div class="sub-font">🌑 農曆: {row['農曆']}   📝 修正農曆: {row['修正農曆']}</div>
                                <div class="sub-font">✨ 星座: {row['星座']}</div>
                                <div style="margin-top: 10px;">
                                    <span class="highlight">{row['歲數']} 歲</span> 
                                    <span style="font-size: 16px; color: #555;">又 {days_mod_row} 天</span>
                                </div>
                                <div style="margin-top: 10px; font-size: 16px; color: #ff4b4b; font-weight: bold;">
                                    距離國曆生日還有: {row['距離下次生日(天)']} 天<br>
                                    距離農曆生日還有: {row['距離下次農曆生日(天)']} 天
                                </div>
                            </div>
                            """
                            st.markdown(html_card, unsafe_allow_html=True)
