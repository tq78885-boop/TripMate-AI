import os
import re
import certifi
import airportsdata

import requests
import pycountry
from dotenv import load_dotenv
load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()



API_KEY = os.getenv("AVIATIONSSTACK_API_KEY")

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "CHINA")



BASE_URL = "https://api.aviationstack.com/v1/flights"


AIRPORTS = airportsdata.load("IATA")

# 原始字典（保持和之前一致，方便对照）
COUNTRY_ALIASES = {
    "中国": ["CN", "中华人民共和国", "China"],
    "美国": ["US", "USA", "United States", "美利坚合众国"],
    "英国": ["UK", "United Kingdom", "不列颠及北爱尔兰联合王国"],
    "俄罗斯": ["RU", "Russian Federation", "俄罗斯联邦"],
    "法国": ["FR", "France", "法兰西共和国"],
    "德国": ["DE", "Germany", "德意志联邦共和国"],
    "日本": ["JP", "Japan"],
    "韩国": ["KR", "Korea", "Republic of Korea", "大韩民国"],
    "加拿大": ["CA", "Canada"],
    "澳大利亚": ["AU", "Australia"],
    "印度": ["IN", "India", "印度共和国"],
    "巴西": ["BR", "Brazil", "巴西联邦共和国"],
    "意大利": ["IT", "Italy", "意大利共和国"],
    "西班牙": ["ES", "Spain", "西班牙王国"],
    "荷兰": ["NL", "Netherlands", "尼德兰王国"],
    "瑞士": ["CH", "Switzerland", "瑞士联邦"],
    "瑞典": ["SE", "Sweden", "瑞典王国"],
    "挪威": ["NO", "Norway", "挪威王国"],
    "丹麦": ["DK", "Denmark", "丹麦王国"],
    "芬兰": ["FI", "Finland", "芬兰共和国"],
    "波兰": ["PL", "Poland", "波兰共和国"],
    "葡萄牙": ["PT", "Portugal", "葡萄牙共和国"],
    "奥地利": ["AT", "Austria", "奥地利共和国"],
    "比利时": ["BE", "Belgium", "比利时王国"],
    "新加坡": ["SG", "Singapore", "新加坡共和国"],
    "马来西亚": ["MY", "Malaysia"],
    "泰国": ["TH", "Thailand", "泰王国"],
    "越南": ["VN", "Vietnam", "越南社会主义共和国"],
    "印度尼西亚": ["ID", "Indonesia"],
    "菲律宾": ["PH", "Philippines", "菲律宾共和国"],
    "新西兰": ["NZ", "New Zealand"],
    "南非": ["ZA", "South Africa", "南非共和国"],
    "墨西哥": ["MX", "Mexico", "墨西哥合众国"],
    "阿根廷": ["AR", "Argentina", "阿根廷共和国"],
    "沙特阿拉伯": ["SA", "Saudi Arabia", "沙特阿拉伯王国"],
    "阿联酋": ["AE", "United Arab Emirates", "阿拉伯联合酋长国"],
    "土耳其": ["TR", "Turkey", "土耳其共和国"],
    "以色列": ["IL", "Israel", "以色列国"],
    "埃及": ["EG", "Egypt", "阿拉伯埃及共和国"]
}

COUNTRY_MAIN_AIRPORT = {
    "中国": ["PEK", "首都国际机场", "北京首都"],
    "美国": ["JFK", "约翰·肯尼迪国际机场", "纽约肯尼迪"],
    "英国": ["LHR", "希思罗机场", "伦敦希思罗"],
    "俄罗斯": ["SVO", "谢列梅捷沃国际机场", "莫斯科谢列梅捷沃"],
    "法国": ["CDG", "夏尔·戴高乐机场", "巴黎戴高乐"],
    "德国": ["FRA", "法兰克福机场", "法兰克福"],
    "日本": ["NRT", "成田国际机场", "东京成田"],
    "韩国": ["ICN", "仁川国际机场", "首尔仁川"],
    "加拿大": ["YYZ", "多伦多皮尔逊国际机场", "多伦多皮尔逊"],
    "澳大利亚": ["SYD", "悉尼金斯福德·史密斯机场", "悉尼"],
    "印度": ["DEL", "英迪拉·甘地国际机场", "新德里"],
    "巴西": ["GRU", "圣保罗瓜鲁柳斯国际机场", "圣保罗瓜鲁柳斯"],
    "意大利": ["FCO", "罗马菲乌米奇诺机场", "罗马菲乌米奇诺"],
    "西班牙": ["MAD", "马德里巴拉哈斯机场", "马德里"],
    "荷兰": ["AMS", "阿姆斯特丹史基浦机场", "阿姆斯特丹史基浦"],
    "瑞士": ["ZRH", "苏黎世机场", "苏黎世"],
    "瑞典": ["ARN", "斯德哥尔摩阿兰达机场", "斯德哥尔摩阿兰达"],
    "挪威": ["OSL", "奥斯陆加勒穆恩机场", "奥斯陆"],
    "丹麦": ["CPH", "哥本哈根凯斯楚普机场", "哥本哈根"],
    "芬兰": ["HEL", "赫尔辛基万塔机场", "赫尔辛基万塔"],
    "波兰": ["WAW", "华沙肖邦机场", "华沙肖邦"],
    "葡萄牙": ["LIS", "里斯本机场", "里斯本"],
    "奥地利": ["VIE", "维也纳国际机场", "维也纳"],
    "比利时": ["BRU", "布鲁塞尔机场", "布鲁塞尔"],
    "新加坡": ["SIN", "新加坡樟宜机场", "樟宜"],
    "马来西亚": ["KUL", "吉隆坡国际机场", "吉隆坡"],
    "泰国": ["BKK", "素万那普机场", "曼谷素万那普"],
    "越南": ["SGN", "胡志明市新山一机场", "胡志明新山一"],
    "印度尼西亚": ["CGK", "雅加达苏加诺-哈达机场", "雅加达"],
    "菲律宾": ["MNL", "马尼拉尼诺·阿基诺机场", "马尼拉"],
    "新西兰": ["AKL", "奥克兰机场", "奥克兰"],
    "南非": ["JNB", "奥利弗·坦博国际机场", "约翰内斯堡"],
    "墨西哥": ["MEX", "墨西哥城贝尼托·胡亚雷斯机场", "墨西哥城"],
    "阿根廷": ["EZE", "布宜诺斯艾利斯埃塞萨机场", "布宜诺斯艾利斯"],
    "沙特阿拉伯": ["RUH", "哈立德国王国际机场", "利雅得"],
    "阿联酋": ["DXB", "迪拜国际机场", "迪拜"],
    "土耳其": ["IST", "伊斯坦布尔新机场", "伊斯坦布尔"],
    "以色列": ["TLV", "本·古里安机场", "特拉维夫"],
    "埃及": ["CAI", "开罗国际机场", "开罗"]
}

CITY_MAIN_AIRPORT = {
    "北京": ["PEK", "首都国际机场", "北京首都"],
    "上海": ["PVG", "浦东国际机场", "上海浦东"],
    "广州": ["CAN", "白云国际机场", "广州白云"],
    "深圳": ["SZX", "宝安国际机场", "深圳宝安"],
    "成都": ["CTU", "双流国际机场", "成都双流"],
    "重庆": ["CKG", "江北国际机场", "重庆江北"],
    "香港": ["HKG", "香港国际机场", "香港"],
    "台北": ["TPE", "桃园国际机场", "台北桃园"],
    "纽约": ["JFK", "约翰·肯尼迪国际机场", "纽约肯尼迪"],
    "伦敦": ["LHR", "希思罗机场", "伦敦希思罗"],
    "莫斯科": ["SVO", "谢列梅捷沃国际机场", "莫斯科谢列梅捷沃"],
    "巴黎": ["CDG", "夏尔·戴高乐机场", "巴黎戴高乐"],
    "法兰克福": ["FRA", "法兰克福机场", "法兰克福"],
    "东京": ["NRT", "成田国际机场", "东京成田"],
    "首尔": ["ICN", "仁川国际机场", "首尔仁川"],
    "多伦多": ["YYZ", "多伦多皮尔逊国际机场", "多伦多皮尔逊"],
    "悉尼": ["SYD", "悉尼金斯福德·史密斯机场", "悉尼"],
    "新德里": ["DEL", "英迪拉·甘地国际机场", "新德里"],
    "圣保罗": ["GRU", "圣保罗瓜鲁柳斯国际机场", "圣保罗瓜鲁柳斯"],
    "罗马": ["FCO", "罗马菲乌米奇诺机场", "罗马菲乌米奇诺"],
    "马德里": ["MAD", "马德里巴拉哈斯机场", "马德里"],
    "阿姆斯特丹": ["AMS", "阿姆斯特丹史基浦机场", "阿姆斯特丹史基浦"],
    "苏黎世": ["ZRH", "苏黎世机场", "苏黎世"],
    "斯德哥尔摩": ["ARN", "斯德哥尔摩阿兰达机场", "斯德哥尔摩阿兰达"],
    "奥斯陆": ["OSL", "奥斯陆加勒穆恩机场", "奥斯陆"],
    "哥本哈根": ["CPH", "哥本哈根凯斯楚普机场", "哥本哈根"],
    "赫尔辛基": ["HEL", "赫尔辛基万塔机场", "赫尔辛基万塔"],
    "华沙": ["WAW", "华沙肖邦机场", "华沙肖邦"],
    "里斯本": ["LIS", "里斯本机场", "里斯本"],
    "维也纳": ["VIE", "维也纳国际机场", "维也纳"],
    "布鲁塞尔": ["BRU", "布鲁塞尔机场", "布鲁塞尔"],
    "新加坡": ["SIN", "新加坡樟宜机场", "樟宜"],
    "吉隆坡": ["KUL", "吉隆坡国际机场", "吉隆坡"],
    "曼谷": ["BKK", "素万那普机场", "曼谷素万那普"],
    "胡志明市": ["SGN", "胡志明市新山一机场", "胡志明新山一"],
    "雅加达": ["CGK", "雅加达苏加诺-哈达机场", "雅加达"],
    "马尼拉": ["MNL", "马尼拉尼诺·阿基诺机场", "马尼拉"],
    "奥克兰": ["AKL", "奥克兰机场", "奥克兰"],
    "约翰内斯堡": ["JNB", "奥利弗·坦博国际机场", "约翰内斯堡"],
    "墨西哥城": ["MEX", "墨西哥城贝尼托·胡亚雷斯机场", "墨西哥城"],
    "布宜诺斯艾利斯": ["EZE", "布宜诺斯艾利斯埃塞萨机场", "布宜诺斯艾利斯"],
    "利雅得": ["RUH", "哈立德国王国际机场", "利雅得"],
    "迪拜": ["DXB", "迪拜国际机场", "迪拜"],
    "伊斯坦布尔": ["IST", "伊斯坦布尔新机场", "伊斯坦布尔"],
    "特拉维夫": ["TLV", "本·古里安机场", "特拉维夫"],
    "开罗": ["CAI", "开罗国际机场", "开罗"]
}




# 反向别名表：别名 -> 标准国名
ALIAS_TO_COUNTRY = {}
for country, alias_list in COUNTRY_ALIASES.items():
    for alias in alias_list:
        ALIAS_TO_COUNTRY[alias] = country

# 反向机场表：机场标识(IATA/全称/简称) -> 标准国名
AIRPORT_TO_COUNTRY = {}
for country, airport_info in COUNTRY_MAIN_AIRPORT.items():
    for item in airport_info:
        AIRPORT_TO_COUNTRY[item] = country

# 反向字典：机场标识(IATA/全称/简称) → 标准城市名
AIRPORT_TO_CITY = {}
for city, airport_info in CITY_MAIN_AIRPORT.items():
    for item in airport_info:
        AIRPORT_TO_CITY[item] = city

def clean_text(text: str) -> str:
    text=text.lower().strip()
    text=re.sub(r"[^a-z0-9\s]", " ",  text)
    text= re.sub(r"\s+", " ", text)
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel"
        "plan", "complete", "days", "day", "including", "hotel"
        "hotels", "sightseeing", "under", "budget", "info","information"
    ]
    
    words = [w for w in text.split() if w not in stop_words]
    return" ".join(words).strip()


def country_name_to_code(text:str):
    text=clean_text(text)

    if text in ALIAS_TO_COUNTRY:
        return ALIAS_TO_COUNTRY[text]
    try:
        country=pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass
    
    # Detect country name inside longer text
    for country in pycountry.countries:
        country_name=country.name.lower()
        if country_name in text:
            return country.alpha_2
    for alias, code in ALIAS_TO_COUNTRY.items():
        if alias in text:
            return code
    return None



def airport_country_matches(airport:dict, country_code:str) -> bool:
    airport_country = str(airport.get("country", "")).upper().strip()
    if airport_country == country_code:
        return True
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True

    except Exception:
        pass
    return False



def get_best_airport_for_country(country_code: str):
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)
    if preferred and preferred in AIRPORTS:
        return preferred
    candidates = []
    for iata,airport in AIRPORTS.items():
        if not iata:
            continue
        if airport_country_matches(airport, country_code):
            name=str(airport.get("name", "")).lower()
            city=str(airport.get("city","")).lower()
            score = 0
            if "international" in name:
                score += 50
            if  "intl" in name:
                score += 40
            if"capital"in name:
                score += 20
            if city:
                score += 5
            candidates.append((score,iata))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]



def resolve_location_to_iata(location:str):
 
    if not location:
        return None
    raw_location = location.strip()
    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}",raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code
    location_clean = clean_text(raw_location)
    if not location_clean:
        return None

    # City preferred airport
    if location_clean in AIRPORT_TO_CITY:
        return AIRPORT_TO_CITY[location_clean]
    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
    if airport:
        return airport

    city_matches = []

    for iata,airport in AIRPORTS.items:
        city = str(airport.get("city",)).lower().strip()
        name = str(airport.get("name","")).lower().strip()
        score = 0
        if city == location_clean:
            score += 100
        elif location_clean in city:
            core += 70
        if location_clean in name:
            score += 50
        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score,iata))

    if  city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]
    return None 


def find_location_mentions(query: str):

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in ALIAS_TO_COUNTRY:
        if re.search(rf"\b{re.escape(alias)}\b",q):
            mentions.append(alias)

    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"/b{re.escape(name)}\b",q):
            mentions.append(name)



    for city in AIRPORT_TO_CITY:
        if re.search(rf"\b{re.escape(city)}\b",q):
            mentions.append(city)
    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions

def parse_route(query: str):
    q = query.strip()
    q_lower=q.lower()
    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]
    if any(keyword in q_lower for keyword in global_keywords):
        return None,None
    # Direct IATA code route:DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)
    if len(codes)>=2:
        dep = codes[0].upper
        arr = codes[1].upper
        return dep,arr
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?=(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$))",
        q_lower,
    )  
    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)
        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)
        return dep_iata,arr_iata
    match = re.search(
        r"\bto\s+(.+?)\s+/bfrom\s+(.+?)(?:\s+(?:on|for|under|inclluding|with|in|at)\b|[.!?]|$)",
        q_lower,
        )  

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)
        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)
        return dep_iata,arr_iata

    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)
    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        return dep_iata, None

    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)


    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None,arr_iata

    mentions = find_location_mentions(q)
    if len(mentions)>=2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata,arr_iata
    if len(mentions)== 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata
    return None,None


def format_flight(flight:dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number=flight.get("flight",{}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep=flight.get("departure",{})or{}
    arr=flight.get("arrival",{})or{}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata=dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate=dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate=arr.get("gate")or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    
    return f"""
Airline:{airline}
Flight:{flight_number}
Status:{status}

Departure:
- Airport:{dep_airport}
- IATA:{dep_iata}
- Terminal:{dep_terminal}
- Gate:{dep_gate}
- Scheduled:{dep_scheduled}
- Delay:{dep_delay_text}

Arrival:
- Airport:{arr_airport} I
- IATA:{arr_iata}
- Terminal:{arr_terminal}
- Gate:{arr_gate}
- Scheduled:{arr_scheduled}
- Delay:{arr_delay_text}
""".strip()

def search_flights(query: str,limit: int = 10):
    if not API_KEY:
        return (
        "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
        "Please add this in your .env file:\n"
        "AVIATIONSTACK_API_KEY=your_api_key_here")
    dep_iata, arr_iata=parse_route(query)

    params = {
    "access_key": API_KEY,
    "limit":min(limit,100),
    }
    if dep_iata:
        params["dep_iata"] = dep_iata
    if arr_iata:
        params["arr_iata"] = arr_iata
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed:{e}"
    except ValueError:
        return "Flight API returned invalid JSON."
    if "error" in data:
        error=data["error"]
        return (
            "Flight API error:\n"
            f"Code:{error.get('code','Unknown')}\n"
            f"Message:{error.get('message')}, 'Unknown error')"
            )
    
    flight_data=data.get("data", [])
    if not flight_data:
        route_text=""
        if not flight_data:
            route_text = ""
        if dep_iata and arr_iata:
            route_text=f" for route {dep_iata} to {arr_iata}" 
        elif dep_iata:
            route_text=f" from{dep_iata}"
        elif arr_iata:
            route_text=f"to{arr_iata}"
        return(
            f"No live flight data found{route_text}.\n\n\n"
        "Note: AviationStack provides live/status flight data, not ticket prices."
        "For actual fare prices, use a flight-pricing API ssuch as Amadeus.")
    route_info="Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info=f"Liveflights from {dep_iata}"
    elif arr_iata:
        route_info=f"Liveflightsto{arr_iata}"
    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]
    return f"{route_info}\n\n"+ "\n\n---\n\n\'".join(formatted_flights)
if __name__== "__main__":
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n"+ "=" * 80 + "\n")
    print(search_flights("all country flight info"))

