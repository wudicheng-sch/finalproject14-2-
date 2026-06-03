from random_point import get_combined_polygon, generate_random_point_in_polygon
from search import search_multiple_poi
from route import filter_by_walking_time
from summary import display_summary


if __name__ == "__main__":
    print("📡 [main] 正在下載校園邊界...")
    combined_polygon = get_combined_polygon([
        "國立清華大學",
        "國立陽明交通大學"
    ])
    
    if combined_polygon:
        # 1. 抽隨機點
        random_center = generate_random_point_in_polygon(combined_polygon)
        print(f"\n🎯 隨機中心起點: ({random_center['lat']:.4f}, {random_center['lon']:.4f})\n")
        
        # 2. 定義要搜尋的地點類型清單
        poi_types = [
            ("[tourism=artwork]", 1.0),
            ("大樓", 0.8),
            ("齋", 0.6),
            ("[amenity=restaurant]", 0.5),
            ("[amenity=cafe]", 0.6)
        ]
        
        # 3. 批量搜尋各種地點（只搜索，不计算步行时间）
        print("🚀 開始搜尋校園內各種地點...\n")
        search_results = search_multiple_poi(poi_types, random_center)
        
        # 4. 顯示摘要
        display_summary(search_results)
        
        # 5. 如果需要計算步行時間，對某個地點進行詳細計算
        print("="*60)
        print("📡 正在計算詳細步行時間...")
        print("="*60 + "\n")
        
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
                    # 按步行時間排序
                    sorted_data = sorted(
                        filtered_data,
                        key=lambda x: x['real_walking_time_min']
                    )
                    
                    print(f"✅ {poi_type} (步行時間 <= 5 分鐘)\n")
                    for i, poi in enumerate(sorted_data, 1):
                        print(f"{i}. {poi['display_name'].split(',')[0]}")
                        print(f"   ├─ 距離: {poi['real_distance_m']} 公尺")
                        print(f"   └─ 時間: {poi['real_walking_time_min']} 分鐘\n")
                else:
                    print(f"❌ {poi_type} - 沒有 5 分鐘內的地點\n")
    else:
        print("❌ 邊界下載失敗")
