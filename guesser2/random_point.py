import random
import requests
from shapely.geometry import shape, Point

def get_university_polygon(university_name: str):
    """
    從 Nominatim API 抓取任意大學的精準 GeoJSON 多邊形
    
    Args:
        university_name: 大學名稱，例如 "國立清華大學" 或 "國立陽明交通大學"
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": university_name,
        "format": "json",
        "limit": 1,
        "polygon_geojson": 1
    }
    headers = {
        "User-Agent": "MyFinalProjectApp/1.0 (113021131nthu@gmail.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and response.json():
            geojson_data = response.json()[0].get("geojson")
            # 使用 shapely 將 GeoJSON 轉換為幾何多邊形物件
            return shape(geojson_data)
        return None
    except Exception as e:
        print(f"抓取 {university_name} 邊界失敗: {e}") 
        return None

def generate_random_point_in_polygon(polygon, max_attempts=1000):
    """
    在任意不規則邊界內，隨機產生一個經緯度點
    
    Args:
        polygon: Shapely 多邊形物件
        max_attempts: 最大嘗試次數
    """
    if not polygon:
        return None
        
    min_lon, min_lat, max_lon, max_lat = polygon.bounds
    
    attempts = 0
    while attempts < max_attempts:
        rand_lon = random.uniform(min_lon, max_lon)
        rand_lat = random.uniform(min_lat, max_lat)
        
        random_point = Point(rand_lon, rand_lat)
        
        if polygon.contains(random_point):
            return {"lat": rand_lat, "lon": rand_lon}
            
        attempts += 1
        
    print("超過最大嘗試次數，無法在邊界內找到隨機點。")
    return None


def get_combined_polygon(university_names: list):
    """
    合併多所大學的邊界成一個聯合多邊形
    
    Args:
        university_names: 大學名稱列表，例如 ["國立清華大學", "國立陽明交通大學"]
    
    Returns:
        聯合後的 Shapely 多邊形物件
    """
    from shapely.geometry import MultiPolygon, Polygon
    from shapely.ops import unary_union
    
    polygons = []
    
    for uni_name in university_names:
        print(f"📡 正在下載 {uni_name} 的邊界...")
        poly = get_university_polygon(uni_name)
        if poly:
            polygons.append(poly)
            print(f"✅ {uni_name} 邊界已載入")
        else:
            print(f"❌ {uni_name} 邊界載入失敗")
    
    if polygons:
        # 合併所有多邊形為一個聯合多邊形
        combined = unary_union(polygons)
        return combined
    
    return None
