import requests

def find_location_by_nominatim_with_bounds(query_string: str, center_lat: float, center_lon: float, radius_km: float = 2.0):
    """
    方法 B：使用 Nominatim API 搜尋地點，並利用 viewbox 強制限制在中心點周邊範圍內
    
    Args:
        query_string: 搜尋關鍵字 (例如: "圖書館")
        center_lat: 區域中心點緯度 (例如: 大學中心點)
        center_lon: 區域中心點經度
        radius_km: 限制搜尋的半徑公里數（預設 2.0 公里）
    """
    url = "https://nominatim.openstreetmap.org/search"
    
    # 簡單估算地理邊界：0.01 度經緯度大約等同於 1 公里
    offset = radius_km * 0.01
    
    # 計算正方形方框的四個極值
    min_lat = center_lat - offset
    max_lat = center_lat + offset
    min_lon = center_lon - offset
    max_lon = center_lon + offset
    
    # Nominatim viewbox 格式規範：西、南、東、北 (lon1, lat1, lon2, lat2)
    viewbox_str = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    
    params = {
        "q": query_string,
        "format": "json",
        "limit": 10,
        "addressdetails": 1,
        "viewbox": viewbox_str,  # 📌 提供搜尋方框
        "bounded": 1             # 📌 強制限制結果必須在方框內，不向外擴展
    }
    
    headers = {
        "User-Agent": "MyFinalProjectApp/1.0 (113021131nthu@gmail.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                results = []
                for item in data:
                    location_data = {
                        "display_name": item.get("display_name"),
                        "lat": float(item.get("lat")),
                        "lon": float(item.get("lon")),
                        "address": item.get("address")
                    }
                    results.append(location_data)
                return results
            else:
                print(f"在限定半徑 {radius_km} 內，找不到與「{query_string}」相符的位置。")
                return None
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"發生連線錯誤: {e}")
        return None


def search_multiple_poi(poi_list: list, random_center: dict):
    """
    批量搜尋多種地點
    
    Args:
        poi_list: 地點清單，格式為 [("地點名稱", 搜尋半徑), ...]
                 例如：[("圖書館", 1.0), ("食堂", 0.8), ...]
        random_center: 起點座標 {"lat": ..., "lon": ...}
    
    Returns:
        dict: 包含所有搜尋結果的字典
    """
    results = {}
    
    for poi_name, radius in poi_list:
        print(f"\n{'='*60}")
        print(f"🔍 正在搜尋: {poi_name}")
        print(f"{'='*60}")
        
        nearby_results = find_location_by_nominatim_with_bounds(
            query_string=poi_name,
            center_lat=random_center['lat'],
            center_lon=random_center['lon'],
            radius_km=radius
        )
        
        if nearby_results:
            print(f"✅ 找到 {len(nearby_results)} 個 {poi_name}")
        else:
            print(f"❌ 未找到 {poi_name}")
        
        results[poi_name] = nearby_results
    
    return results
