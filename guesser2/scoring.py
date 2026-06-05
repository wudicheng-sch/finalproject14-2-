import folium
from search import find_location_by_nominatim_with_bounds 
from flask import render_template_string
from route import get_walking_time_and_route

def generate_answer_map(target_place: dict, player_guess: dict):
    """
    對答案地圖生成函式
    輸入：
      - target_place: 正解字典 (包含 lat, lon, address 等)
      - player_guess: 玩家猜測地點字典
    回傳：
      - folium.Map 物件的 HTML 字串，方便 Flask 直接渲染
    """
    # 提取正解與猜測點的經緯度
    t_lat, t_lon = target_place['lat'], target_place['lon']
    g_lat, g_lon = player_guess['lat'], player_guess['lon']
    
    # 提取顯示名稱（優先使用 amenity，其次為 display_name）
    t_name = target_place['address'].get('amenity', target_place['display_name'].split(',')[0])
    g_name = player_guess['address'].get('amenity', player_guess['display_name'].split(',')[0])
    
    # 1. 呼叫你現有的 OSRM 路由函式取得時間與距離
    # 註：此處假設你的 get_walking_time_and_route 已經在外部定義好
    osrm_data = get_walking_time_and_route(t_lat, t_lon, g_lat, g_lon)
    
    if osrm_data:
        walking_time = osrm_data.get("walking_time_min", 0)
        distance = osrm_data.get("real_distance_m", 0)
    else:
        walking_time = "未知"
        distance = "未知"
        
    # 2. 初始化 Folium 地圖，將中心點定在兩點的中心
    center_lat = (t_lat + g_lat) / 2
    center_lon = (t_lon + g_lon) / 2
    mymap = folium.Map(location=[center_lat, center_lon], zoom_start=16)
    
    # 3. 標註正解（紅色 Pin）
    t_popup_text = f"<b>🎯 正確答案：{t_name}</b>"
    folium.Marker(
        location=[t_lat, t_lon],
        popup=folium.Popup(t_popup_text, max_width=300),
        tooltip=f"正確答案: {t_name}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(mymap)
    
    # 4. 標註玩家猜測（藍色 Pin）
    g_popup_text = f"<b>🤔 你的猜測：{g_name}</b>"
    folium.Marker(
        location=[g_lat, g_lon],
        popup=folium.Popup(g_popup_text, max_width=300),
        tooltip=f"你的猜測: {g_name}",
        icon=folium.Icon(color='blue', icon='user')
    ).add_to(mymap)
    
    # 5. 畫出兩者相連的直線路徑（並在路徑上標註通行時間與距離）
    route_line = folium.PolyLine(
        locations=[[t_lat, t_lon], [g_lat, g_lon]],
        color='purple',
        weight=4,
        opacity=0.7,
        dash_array='5, 10' # 虛線樣式，看起來更像對答案的延伸線
    ).add_to(mymap)
    
    # 在線條的中央加上資訊彈窗 (Popup)，點擊線條就能看到時間與距離
    info_popup = f"<b>🚶 實際步行距離：</b>{distance} 公尺<br><b>⏰ 預估步行時間：</b>{walking_time} 分鐘"
    route_line.add_child(folium.Popup(info_popup, max_width=250))
    
    # 6. 回傳地圖的 HTML 原始碼字串
    return mymap._repr_html_()
 
