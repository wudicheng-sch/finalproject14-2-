import os
from flask import Flask, render_template_string, request, session, redirect
import folium
from scoring import generate_answer_map
from data_setting import data_setting
from search import find_location_by_nominatim_with_bounds
from game_setting import generate_question_map_mode_one
from route import get_walking_time_and_route
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 使用 Session 必須設定金鑰

# ==================== Flask 路由實作 ====================

@app.route('/')
def index():
    """ 主選單：可以選擇進入模式一或模式二 """
    session['current_game_data'] = data_setting()
    
    menu_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>清交Guesser - 主選單</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; text-align: center; padding-top: 50px; }
            .menu-box { max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            .btn { display: block; padding: 15px; margin: 20px 0; font-size: 18px; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }
            .btn-one { background-color: #3498db; }
            .btn-two { background-color: #e67e22; }
        </style>
    </head>
    <body>
        <div class="menu-box">
            <h1>🧩 清交Guesser 🧩</h1>
            <p>考驗你對校園周邊地理位置的敏銳度！</p>
            <hr>
            <a href="/play_mode_one" class="btn btn-one">進入 模式一：空間相對位置猜謎 🗺️</a>
            <a href="/play_mode_two" class="btn btn-two">進入 模式二：步行時間線索猜謎 ⏱️</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(menu_template)


@app.route('/play_mode_one', methods=['GET'])
def play_mode_one_view():
    """ 模式一：出題畫面（顯示模糊的 Folium 地圖） """
    game_data = session.get('current_game_data')
    if not game_data or len(game_data) < 2:
        return "遊戲資料不足，請重新開始。"

    target_place = game_data[0]
    hint_places = game_data[1:]
    
    # 生成模式一的模糊出題地圖 HTML
    map_html = generate_question_map_mode_one(target_place, hint_places)

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>清交Guesser - 模式一</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; text-align: center; padding: 20px; }
            .card { background: white; max-width: 850px; margin: 0 auto; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            .map-container { width: 100%; height: 500px; margin: 20px 0; border: 2px solid #ccc; border-radius: 8px; overflow: hidden; }
            input[type="text"] { width: 60%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; }
            button { padding: 10px 20px; font-size: 16px; background-color: #2ecc71; color: white; border: none; border-radius: 6px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎮 模式一：地圖空間解謎</h1>
            <p><b>【遊戲玩法】</b>地圖上已隱去路名。觀察<b>綠色提示點（有名字）</b>與<b>紅色神秘點（目標答案）</b>的相對位置，猜出紅點是哪裡！</p>
            
            <div class="map-container">
                {{ map_html|safe }}
            </div>
            
            <form action="/check_answer" method="POST">
                <input type="text" name="player_guess" placeholder="輸入你猜測的紅點建築/餐廳名稱..." required autocomplete="off">
                <button type="submit">送出答案 🏁</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, map_html=map_html)


@app.route('/play_mode_two', methods=['GET'])
def play_mode_two_view():
    """ 模式二：出題與提示畫面（無地圖） """
    game_data = session.get('current_game_data')
    if not game_data or len(game_data) < 2:
        return "遊戲資料不足，請重新開始。"

    # 解析資料
    target_place = game_data[0]
    hint_places = game_data[1:]
    
    # 建立要渲染給前端的提示清單
    hints_to_show = []
    for hint in hint_places:
        hint_name = hint['address'].get('amenity', hint['display_name'].split(',')[0])
        hints_to_show.append({
            "name": hint_name,
            "time": hint['real_walking_time_min'],
            "distance": hint['real_distance_m']
        })

    # HTML 樣板：出題畫面 (無地圖模式)
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>清交Guesser - 模式二</title>
        <style>
            body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f7f6; color: #333; text-align: center; padding: 40px; }
            .card { background: white; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            h1 { color: #2c3e50; }
            ul { list-style-type: none; padding: 0; text-align: left; }
            li { background: #eef2f5; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 5px solid #3498db; }
            input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; margin-top: 20px; }
            button { padding: 10px 20px; font-size: 16px; background-color: #2ecc71; color: white; border: none; border-radius: 6px; cursor: pointer; }
            button:hover { background-color: #27ae60; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎮 清交Guesser | 模式二：時間解謎</h1>
            <p><b>【遊戲提示】</b>以下是數個「提示地標」走到「目標地標」所需的步行時間。請猜出目標地標是哪裡！</p>
            <hr>
            <ul>
                {% for hint in hints %}
                <li>📍 從 <b>【{{ hint.name }}】</b> 走到目標地標需要：<br>⏱️ <b>{{ hint.time }}</b> 分鐘 (約 {{ hint.distance }} 公尺)</li>
                {% endfor %}
            </ul>
            <form action="/check_answer" method="POST">
                <input type="text" name="player_guess" placeholder="輸入你猜測的建築物/餐廳名稱..." required autocomplete="off">
                <br><br>
                <button type="submit">送出答案 🏁</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, hints=hints_to_show)


@app.route('/check_answer', methods=['POST'])
def check_answer_view():
    """ 模式二：對答案與結果判定（顯示 Folium 地圖） """
    game_data = session.get('current_game_data')
    player_guess_name = request.form.get('player_guess', '').strip()
    
    if not game_data:
        return redirect('/')

    target_place = game_data[0]
    target_name = target_place['address'].get('amenity', target_place['display_name'].split(',')[0])
    
    # 1. 判定勝負 (模糊比對)
    is_correct = player_guess_name.lower() in target_name.lower() or target_name.lower() in player_guess_name.lower()
    
    
    # 2. 建立玩家猜測的地點字典 (為了丟給地圖函式畫出兩點)
    # 如果猜對了，地點座標就等於正解。
    if is_correct:
        player_guess_dict = target_place
        score = 100
        status = "success"
        show_guess_name = True
        error_hint = ""
    else:
        # 如果答錯了，在實際期末專案中，你可以在這邊串 Nominatim API 去搜尋 player_guess_name 的座標。
        # 這裡先抓題庫裡的「第二筆資料」作為玩家猜錯的代表座標，或者你可以放一個預設的清大校門口座標。
        if find_location_by_nominatim_with_bounds(player_guess_name,target_place['lat'],target_place["lon"],2)==None:
            # 玩家猜錯且無法被搜尋到：不顯示玩家回答、加上提示
            show_guess_name = False
            error_hint = "⚠️ 無法辨認答案"
            player_guess_dict = game_data[1].copy() 
            player_guess_dict['address']['amenity'] = player_guess_name if show_guess_name else "未知位置"
            score = 0
        else:
            # 玩家猜錯但地點存在
            show_guess_name = True
            error_hint = ""
            player_guess_dict = find_location_by_nominatim_with_bounds(player_guess_name,target_place['lat'],target_place["lon"],2)[0] 
            # 修改名稱為玩家輸入的名稱，以便在地圖上顯示
            player_guess_dict['address']['amenity'] = player_guess_name
            t_lat, t_lon = target_place['lat'], target_place['lon']
            g_lat, g_lon = player_guess_dict['lat'], player_guess_dict['lon']
    
            # 1. 呼叫你現有的 OSRM 路由函式取得時間與距離
            # 註：此處假設你的 get_walking_time_and_route 已經在外部定義好
            osrm_data = get_walking_time_and_route(t_lat, t_lon, g_lat, g_lon)
    
            if osrm_data:
                distance = osrm_data.get("real_distance_m", 0)
            else:
                distance = 0
            score = 100 if is_correct else math.floor(100*(2.8**(-((distance/515)**1.5))))
            # 提取正解與猜測點的經緯度 
        
    map_html = generate_answer_map(target_place, player_guess_dict)

    # HTML 樣板：對答案畫面 (內嵌地圖)
    result_template = result_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>清交Guesser - 對答案結果</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; text-align: center; padding: 20px; }
            .result-box { max-width: 850px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            .success { color: #2ecc71; }
            .fail { color: #e74c3c; }
            .hint-text { color: #e67e22; font-weight: bold; font-size: 18px; margin: 10px 0; }
            .map-container { width: 100%; height: 500px; margin-top: 20px; border: 2px solid #ddd; border-radius: 8px; overflow: hidden; }
        </style>
    </head>
    <body>
        <div class="result-box">
            <h1>🏁 對答案時間 🏁</h1>
            
            {% if status == 'success' %}
                <h2 class="success">🎉 答對了！本局得分：{{ score }} 分</h2>
            {% else %}
                <h2 class="fail">❌ 答錯囉！本局得分：{{ score }} 分</h2>
            {% endif %}
            
            {% if error_hint %}
                <p class="hint-text">{{ error_hint }}</p>
            {% endif %}
            
            <hr>
            
            {% if show_guess_name %}
                <p>你輸入的是：【{{ player_guess_name }}】</p>
            {% endif %}
            
            <p>💡 正確答案其實是：<b>【{{ target_name }}】</b></p>
            
            <div class="map-container">
                {{ map_html|safe }}
            </div>
            <a href="/" style="display:inline-block; margin-top:20px; padding:10px 20px; background:#34495e; color:white; text-decoration:none; border-radius:6px;">回主選單 🔁</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        result_template, 
        is_correct=is_correct, 
        score=score, 
        target_name=target_name, 
        player_guess_name=player_guess_name, 
        map_html=map_html
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
