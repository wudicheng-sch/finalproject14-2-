import folium


def generate_question_map_mode_one(target_place: dict, hint_places: list):
    """
    模式一：生成模糊的出題地圖
    - 答案：紅色 Pin (不寫名字，只有代號)
    - 提示：綠色 Pin (標註名字)
    - 圖磚：Cartodb Positron (極簡無干擾地圖)
    """
    t_lat, t_lon = target_place['lat'], target_place['lon']
    
    # 計算地圖中心點 (所有點的平均值)
    all_lats = [t_lat] + [h['lat'] for h in hint_places]
    all_lons = [t_lon] + [h['lon'] for h in hint_places]
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # 使用 tiles="Cartodb Positron" 隱藏地圖上的地名與商家資訊
    mymap = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles=None)
    
    # 1. 標註答案（紅色 Pin，隱藏真實名稱）
    folium.Marker(
        location=[t_lat, t_lon],
        popup="<b>❓ 神秘目標地點</b>",
        tooltip="目標地點 (??? )",
        icon=folium.Icon(color='red', icon='question-sign')
    ).add_to(mymap)
    
    # 2. 標註提示地點（綠色 Pin，顯示名稱）
    for hint in hint_places:
        h_lat, h_lon = hint['lat'], hint['lon']
        h_name = hint['address'].get('amenity', hint['display_name'].split(',')[0])
        
        folium.Marker(
            location=[h_lat, h_lon],
            popup=f"<b>📍 提示點：{h_name}</b>",
            tooltip=h_name,
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(mymap)
        
    return mymap._repr_html_()