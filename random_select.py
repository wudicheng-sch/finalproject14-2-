import random

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

