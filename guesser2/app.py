import os
from flask import Flask, render_template, request, session, redirect
import folium
from scoring import generate_answer_map
from data_setting import data_setting
from search import find_location_by_nominatim_with_bounds
from game_setting import generate_question_map_mode_one
from route import get_walking_time_and_route
from calculate_distance import calculate_distance
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 使用 Session 必須設定金鑰

# ==================== Flask 輔助函式 ====================

def render_error_page(message):
    
    return render_template("error.html", message=message)

# ==================== Flask 路由實作 ====================

@app.route('/')
def index():
    """ 主選單：開始遊戲或查看規則說明 """
    
    return render_template("index.html")



@app.route('/start_game')
def start_game_view():
    """ 遊戲開始頁面：選擇模式一或模式二 """
    session['current_game_data'] = data_setting()
    
    return render_template("start_game_view.html")


@app.route('/rules')
def rules_view():
    """ 顯示遊戲規則說明頁面 """
    return render_template("rules_view.html")


@app.route('/play_mode_one', methods=['GET'])
def play_mode_one_view():
    """ 模式一：出題畫面（顯示模糊的 Folium 地圖） """
    game_data = session.get('current_game_data')
    if not game_data or len(game_data) < 2:
        return render_error_page("目前遊戲資料不足，請點選「回到主選單」重新開始。")

    target_place = game_data[0]
    hint_places = game_data[1:]
    
    # 生成模式一的模糊出題地圖 HTML
    map_html = generate_question_map_mode_one(target_place, hint_places)
    return render_template("play_mode_one_view.html", map_html=map_html)


@app.route('/play_mode_two', methods=['GET'])
def play_mode_two_view():
    """ 模式二：出題與提示畫面（無地圖） """
    game_data = session.get('current_game_data')
    if not game_data or len(game_data) < 2:
        return render_error_page("目前遊戲資料不足，請點選「回到主選單」重新開始。")

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
    return render_template("play_mode_two_view.html", hints=hints_to_show)


@app.route('/check_answer', methods=['POST'])
def check_answer_view():
    """ 對答案與結果判定（顯示 Folium 地圖） """
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
        distance = 0
    else:
        # 如果答錯了，在實際期末專案中，你可以在這邊串 Nominatim API 去搜尋 player_guess_name 的座標。
        # 這裡先嘗試使用 Nominatim 搜尋玩家輸入的地點。
        search_results = find_location_by_nominatim_with_bounds(player_guess_name, target_place['lat'], target_place['lon'], 2)
        if not search_results:
            # 玩家猜錯且無法被搜尋到：未知位置，不顯示在地圖上
            show_guess_name = False
            error_hint = "⚠️ 無法辨認答案"
            player_guess_dict = None
            score = 0
            distance = None
        else:
            # 玩家猜錯但地點存在
            show_guess_name = True
            error_hint = ""
            player_guess_dict = search_results[0].copy()
            # 修改名稱為玩家輸入的名稱，以便在地圖上顯示
            player_guess_dict['address']['amenity'] = player_guess_name
            t_lat, t_lon = target_place['lat'], target_place['lon']
            g_lat, g_lon = player_guess_dict['lat'], player_guess_dict['lon']

            # 取得兩點之間的直線距離
            distance = calculate_distance(t_lat, t_lon, g_lat, g_lon)
            score = 100 if is_correct else math.floor(100 * (2.8 ** (-(distance / 515) ** 1.5)))

    if score >= 90:
        feedback_detail = "太棒了！你對校園地理位置掌握得非常精準。"
    elif score >= 70:
        feedback_detail = "不錯！你很接近目標，再多練習就能更穩定。"
    elif score >= 50:
        feedback_detail = "還行，但你可以再多觀察提示，下一次有機會更高分。"
    else:
        feedback_detail = "加油！這次答案落差較大，下次試著參考提示再來挑戰。"

    map_html = generate_answer_map(target_place, player_guess_dict)

    # HTML 樣板：對答案畫面 (內嵌地圖)
    return render_template(
        "check_answer_view.html",
        is_correct=is_correct, 
        score=score, 
        target_name=target_name, 
        player_guess_name=player_guess_name, 
        map_html=map_html,
        feedback_detail=feedback_detail,
        distance=distance
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
