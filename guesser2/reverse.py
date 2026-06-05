import time
import requests

def reverse_geocode_point(lat: float, lon: float):
    """將經緯度丟入 Nominatim /reverse 端點，並只回傳自訂格式的最近地點資訊"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "accept-language": "zh-TW",
        "zoom": 18,  # 18 為最精確（建築物/門牌級別）
    }
    headers = {
        "User-Agent": "MyFinalProjectApp/1.0 (113021131nthu@gmail.com)"
    }

    try:
        time.sleep(1)  # 遵守每秒 1 次請求的政策
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            item = response.json()

            # 檢查 Nominatim 是否有回傳錯誤訊息（例如查到海面上無地點）
            if "error" in item:
                print(f" Nominatim 提示: {item['error']}")
                return None

            # 💡 依據你的需求，重新建立並回傳指定的格式
            return {
                "display_name": item.get("display_name"),
                "lat": float(item.get("lat")) if item.get("lat") else None,
                "lon": float(item.get("lon")) if item.get("lon") else None,
                "address": item.get("address"),
            }
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            return None
    except Exception as e:
        print(f"反查地點時發生錯誤: {e}")
        return None
