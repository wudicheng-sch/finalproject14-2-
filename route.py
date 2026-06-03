import requests

def get_walking_time_and_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """
    使用 OSRM API (Foot 模式) 計算兩點間的實際步行時間與路線距離
    """
    coordinates_str = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"http://router.project-osrm.org/route/v1/foot/{coordinates_str}"
    
    params = {
        "overview": "false",
        "steps": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                best_route = data["routes"][0]
                duration_seconds = best_route.get("duration", 0)
                distance_meters = best_route.get("distance", 0)
                
                return {
                    "walking_time_min": round(duration_seconds / 60, 1),
                    "real_distance_m": round(distance_meters, 1)
                }
        return None
    except Exception as e:
        print(f"OSRM API 連線錯誤: {e}")
        return None


def process_campus_buildings_with_osrm(buildings_list, university_lat, university_lon):
    """
    將 Nominatim 搜尋到的建築物清單，逐一串接 OSRM 計算實際步行時間
    """
    if not buildings_list:
        return []
        
    updated_results = []
    for building in buildings_list:
        b_lat = building["lat"]
        b_lon = building["lon"]
        
        osrm_data = get_walking_time_and_route(university_lat, university_lon, b_lat, b_lon)
        
        if osrm_data:
            building["real_walking_time_min"] = osrm_data["walking_time_min"]
            building["real_distance_m"] = osrm_data["real_distance_m"]
        else:
            building["real_walking_time_min"] = None
            building["real_distance_m"] = None
            
        updated_results.append(building)
        
    return updated_results

def filter_by_walking_time(buildings_list: list, center_lat: float, center_lon: float, max_time_min: float = 5.0):
    """
    篩選掉步行時間超過指定時間的地點
    
    Args:
        buildings_list: 建築物清單
        center_lat: 起點緯度
        center_lon: 起點經度
        max_time_min: 最大步行時間（分鐘，預設 5.0）
    
    Returns:
        list: 篩選後的結果，只包含步行時間 <= max_time_min 的地點
    """
    if not buildings_list:
        return []
    
    # 先計算所有地點的步行時間
    final_data = process_campus_buildings_with_osrm(
        buildings_list=buildings_list,
        university_lat=center_lat,
        university_lon=center_lon
    )
    
    # 篩選：只保留步行時間 <= max_time_min 的地點
    filtered_data = [
        poi for poi in final_data 
        if poi['real_walking_time_min'] is not None and poi['real_walking_time_min'] <= max_time_min
    ]
    
    return filtered_data
