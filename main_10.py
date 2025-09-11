# 使用文件读入JSON数据的方式处理单个员工

from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(
    api_key="sk-fc28bd037f5744ed9daf31dcc7feb6a3",
    base_url="https://api.deepseek.com"
)

system_content = """
你是一个职工健康提示小助手，
主要任务时结合员工活动时间的数据（如工位久坐时长），生成个性化健康提醒与建议（如休息、补水、运动）。

请根据提供的员工健康数据生成个性化的健康提醒：
1. 首先确认员工身份（姓名、部门、编号、工位信息）
2. 根据喝水杯数进行喝水提醒：
   - 如果喝水不足8杯，提示员工及时补充水源摄入
   - 如果已经喝了8杯或以上，表扬他们并提示要坚持这样的好习惯
3. 根据久坐起始时间和当前时间，计算连续坐的时间：
   - 如果坐着的时间不短于2个小时，提示员工不要久坐，起身活动至少10分钟
   - 如果坐着的时间小于2小时，提示员工不要久坐，每隔一段时间要起身活动一下

你的语气要平易近人，根据员工给出的数据进行合理的提示。
当前时间：{current_time}
"""


def calculate_sit_duration(sit_start_time):
    """
    计算久坐时长（小时）
    """
    try:
        start_time = datetime.strptime(sit_start_time, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        duration = (current_time - start_time).total_seconds() / 3600
        return duration

    except Exception as e:
        print(f"计算久坐时长时出错：{e}")
        return 0


def generate_health_tips(employee_data):
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备系统消息，包含当前时间
    system_msg = system_content.format(current_time=current_time)

    # 计算久坐时长
    sit_duration = calculate_sit_duration(employee_data.get("sit_start_time", ""))
    employee_data["sit_duration_hours"] = round(sit_duration, 2)

    # 将员工数据转化为JSON字符串
    employee_data_str = json.dumps(employee_data, ensure_ascii=False, indent=2)

    messages = [
        {
            "role": "system",
            "content": system_msg
        },
        {
            "role": "user",
            "content": f"以下是员工的健康数据，请生成相应的健康提示: \n{employee_data_str}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
            temperature=1
        )

        ai_response = response.choices[0].message.content
        return ai_response

    except Exception as e:
        return f"调用API时出现错误: {e}"


if __name__ == "__main__":
    # 从文件读取JSON数据的示例
    with open("single_employee_data.json", "r", encoding="utf-8") as f:
        employee_data = json.load(f)
        health_tips = generate_health_tips(employee_data)
        print("健康提示: ")
        print(health_tips)
