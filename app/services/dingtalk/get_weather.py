import requests
import json5

def get_amap_weather(amap_api_key, city="北京", extensions="all"):
    """
    调用高德地图API获取天气数据
    :param amap_api_key: 你的高德API Key
    :param city: 城市名或城市ID（默认“北京”）
    :param extensions: 返回数据类型（默认“all”，实时+7天预报）
    :return: 解析后的结构化天气数据（字典）
    """
    # 高德天气API请求URL
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    # 请求参数
    params = {
        "key": amap_api_key,
        "city": city,
        "extensions": "base",
        "output": "JSON"
    }

    try:
        # 发送GET请求
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 若状态码非200，抛出异常

        # 解析JSON数据
        weather_data = response.json()

        # 检查API返回状态（高德API用“status”字段标识成功与否，1=成功，0=失败）
        if weather_data["status"] != "1":
            raise Exception(f"高德API调用失败：{weather_data.get('info', '未知错误')}")

        # 提取关键数据（实时天气+7天预报，按需简化）
        result = {
            "城市": weather_data["lives"][0]["city"] if "lives" in weather_data else city,
            "实时天气": {
                "温度(℃)": weather_data["lives"][0]["temperature"],
                "天气状况": weather_data["lives"][0]["weather"],
                "湿度(%)": weather_data["lives"][0]["humidity"],
                "风力": weather_data["lives"][0]["windpower"],
                "更新时间": weather_data["lives"][0]["reporttime"]
            }
        }
        return result

    except Exception as e:
        return f"获取天气数据失败：{str(e)}"


if __name__ == "__main__":
    # 获取天气数据
    weather_info = get_amap_weather(AMAP_API_KEY, city="江苏", extensions="all")

    #print("高德地图获取的天气数据：")
    #print(json5.dumps(weather_info, indent=2, ensure_ascii=False))