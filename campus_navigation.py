import requests
from math import radians, sin, cos, sqrt, atan2

def find_location_by_nominatim(query_string: str):
    """
    使用 Nominatim API 將地址或地名轉換為經緯度
    """
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": query_string,
        "format": "json",
        "limit": 5,
        "addressdetails": 1
    }
    
    headers = {
        "User-Agent": "MyFinalProjectApp/1.0 (your_email@example.com)"
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
                print(f"找不到與「{query_string}」相符的位置。")
                return None
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"發生連線錯誤: {e}")
        return None


def get_walking_time_and_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """
    使用 OSRM API (Foot 模式) 計算兩點間的實際步行時間與路線距離
    """
    # OSRM 的座標格式為: {lon},{lat};{lon},{lat} (注意：經度在前，緯度在後)
    coordinates_str = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    
    # 使用 foot 模式（步行）進行導航路由
    url = f"http://router.project-osrm.org/route/v1/foot/{coordinates_str}"
    
    # 參數設定：overview=false 表示不需要回傳完整的地圖繪製幾何線條（加速回應）
    params = {
        "overview": "false",
        "steps": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "Ok" and data.get("routes"):
                # 取得第一條最優路線
                best_route = data["routes"][0]
                
                # OSRM 回傳的 duration 單位為「秒」，distance 單位為「公尺」
                duration_seconds = best_route.get("duration", 0)
                distance_meters = best_route.get("distance", 0)
                
                return {
                    "walking_time_min": round(duration_seconds / 60, 1),  # 換算成分鐘
                    "real_distance_m": round(distance_meters, 1)           # 實際步行距離
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
        
        # 呼叫 OSRM 函式
        osrm_data = get_walking_time_and_route(university_lat, university_lon, b_lat, b_lon)
        
        if osrm_data:
            # 將實際步行數據整合進原本的資料結構中
            building["real_walking_time_min"] = osrm_data["walking_time_min"]
            building["real_distance_m"] = osrm_data["real_distance_m"]
        else:
            building["real_walking_time_min"] = None
            building["real_distance_m"] = None
            
        updated_results.append(building)
        
    return updated_results


def search_and_calculate_walking_time(building_name: str, university_name: str, 
                                      university_lat: float, university_lon: float):
    """
    完整流程：搜尋建築物 + 計算步行時間
    
    Args:
        building_name: 要搜尋的建築物名稱
        university_name: 大學名稱
        university_lat: 大學中心點緯度
        university_lon: 大學中心點經度
    
    Returns:
        包含建築物資訊和步行時間的列表
    """
    print(f"正在搜尋 {building_name}...")
    
    # 第一步：使用 Nominatim 搜尋建築物
    buildings = find_location_by_nominatim(building_name)
    
    if not buildings:
        print(f"找不到 {building_name}")
        return None
    
    print(f"找到 {len(buildings)} 個搜尋結果，正在計算步行時間...\n")
    
    # 第二步：使用 OSRM 計算步行時間
    results_with_walking_time = process_campus_buildings_with_osrm(
        buildings, university_lat, university_lon
    )
    
    return results_with_walking_time


# --- 測試程式碼 ---
if __name__ == "__main__":
    # 設定清華大學的中心點座標（新竹校區主要入口）
    tsinghua_lat = 24.7975
    tsinghua_lon = 120.9954
    
    # 搜尋目標建築物
    target_building = "圖書館"
    
    # 執行搜尋 + 計算步行時間
    results = search_and_calculate_walking_time(
        target_building, 
        "國立清華大學", 
        tsinghua_lat, 
        tsinghua_lon
    )
    
    # 輸出結果
    if results:
        print("=" * 80)
        print(f"【搜尋結果：{target_building}】")
        print("=" * 80)
        
        for i, res in enumerate(results, 1):
            print(f"\n【結果 {i}】")
            print(f"建築物名稱: {res['display_name'].split(',')[0]}")
            print(f"完整地址: {res['display_name']}")
            print(f"座標: ({res['lat']}, {res['lon']})")
            
            if res['real_distance_m'] is not None:
                print(f"從清華大學中心點出發:")
                print(f"  ├─ 實際步行距離: {res['real_distance_m']} 公尺")
                print(f"  └─ 實際步行時間: {res['real_walking_time_min']} 分鐘")
            else:
                print(f"  ├─ 無法計算步行時間")
    else:
        print("查詢失敗，請檢查輸入參數。")
