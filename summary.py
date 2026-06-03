def display_summary(results_dict: dict):
    """
    顯示搜尋結果的摘要
    """
    print("\n" + "="*60)
    print("📊 搜尋結果摘要")
    print("="*60 + "\n")
    
    total_found = 0
    
    for poi_type, results in results_dict.items():
        if results:
            count = len(results)
            total_found += count
            print(f"✅ {poi_type}")
            print(f"   └─ 共找到 {count} 個\n")
        else:
            print(f"❌ {poi_type} - 找不到\n")
    
    print(f"📈 總共找到: {total_found} 個地點\n")
