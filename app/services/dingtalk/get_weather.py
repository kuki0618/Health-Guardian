import requests
import json5

def get_amap_weather(amap_api_key, city="����", extensions="all"):
    """
    ���øߵµ�ͼAPI��ȡ��������
    :param amap_api_key: ��ĸߵ�API Key
    :param city: �����������ID��Ĭ�ϡ���������
    :param extensions: �����������ͣ�Ĭ�ϡ�all����ʵʱ+7��Ԥ����
    :return: ������Ľṹ���������ݣ��ֵ䣩
    """
    # �ߵ�����API����URL
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    # �������
    params = {
        "key": amap_api_key,
        "city": city,
        "extensions": "base",
        "output": "JSON"
    }

    try:
        # ����GET����
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # ��״̬���200���׳��쳣

        # ����JSON����
        weather_data = response.json()

        # ���API����״̬���ߵ�API�á�status���ֶα�ʶ�ɹ����1=�ɹ���0=ʧ�ܣ�
        if weather_data["status"] != "1":
            raise Exception(f"�ߵ�API����ʧ�ܣ�{weather_data.get('info', 'δ֪����')}")

        # ��ȡ�ؼ����ݣ�ʵʱ����+7��Ԥ��������򻯣�
        result = {
            "����": weather_data["lives"][0]["city"] if "lives" in weather_data else city,
            "ʵʱ����": {
                "�¶�(��)": weather_data["lives"][0]["temperature"],
                "����״��": weather_data["lives"][0]["weather"],
                "ʪ��(%)": weather_data["lives"][0]["humidity"],
                "����": weather_data["lives"][0]["windpower"],
                "����ʱ��": weather_data["lives"][0]["reporttime"]
            }
        }
        return result

    except Exception as e:
        return f"��ȡ��������ʧ�ܣ�{str(e)}"


if __name__ == "__main__":
    # ��ȡ��������
    weather_info = get_amap_weather(AMAP_API_KEY, city="����", extensions="all")

    #print("�ߵµ�ͼ��ȡ���������ݣ�")
    #print(json5.dumps(weather_info, indent=2, ensure_ascii=False))