from random_point import get_combined_polygon, generate_random_point_in_polygon
from search import search_multiple_poi
from route import filter_by_walking_time
from summary import display_summary
import random

combined_polygon = get_combined_polygon([
    "國立清華大學",
    "國立陽明交通大學"
])

def select_random_poi(filtered_data: list, count: int = 5):
    """
    從篩選後的地點清單中隨機選出指定數量的地點
    
    Args:
        filtered_data: 篩選後的地點清單
        count: 要選出的地點數量（預設 5）
    
    Returns:
        list: 隨機選出的地點清單，若地點數量不足則返回全部
    """
    if not filtered_data:
        return []
    
    # 如果地點數量少於要求的數量，則返回全部
    if len(filtered_data) <= count:
        return filtered_data
    
    # 隨機選出 count 個地點
    return random.sample(filtered_data, count)

def data_setting():
    if combined_polygon:
        # 1. 抽隨機點
        random_center = generate_random_point_in_polygon(combined_polygon)
        
        # 2. 定義要搜尋的地點類型清單
        poi_types = [
            ("[tourism=artwork]", 1.0),
            ("大樓", 0.8),
            ("齋", 0.6),
            ("[amenity=restaurant]", 0.5),
            ("[amenity=cafe]", 0.6)
        ]

        search_results = search_multiple_poi(poi_types, random_center)
        
    # 3. 顯示摘要
        display_summary(search_results)

    
        all_filtered_data = []  # ✅ 存放所有篩選後的地點
    
        for poi_type, results in search_results.items():
            if results:
                # 篩選步行時間 <= 5 分鐘的地點
                filtered_data = filter_by_walking_time(
                    buildings_list=results,
                    center_lat=random_center['lat'],
                    center_lon=random_center['lon'],
                    max_time_min=5.0
                )
            
                if filtered_data:
                    all_filtered_data.extend(filtered_data)  # ✅ 將篩選結果加入總清單
                else:
                    print(f"❌ {poi_type} - 沒有 5 分鐘內的地點")
            else:
                print(f"❌ {poi_type} - 沒有找到地點")
    
        # 5. 從所有篩選後的地點中隨機選出 5 個
    
    
        random_selected = select_random_poi(all_filtered_data, count=5)
    
        if random_selected:
            # 按步行時間排序
            sorted_data = sorted(
                random_selected,
                key=lambda x: x['real_walking_time_min']
            )
        
            for i, poi in enumerate(sorted_data, 1):
                print(f"{i}. {poi['display_name'].split(',')[0]}")
                print(f"   ├─ 距離: {poi['real_distance_m']} 公尺")
                print(f"   └─ 時間: {poi['real_walking_time_min']} 分鐘\n")
            return sorted_data
        
        else:
            print("❌ 沒有篩選出任何地點")
    else:
        print("❌ 邊界下載失敗")