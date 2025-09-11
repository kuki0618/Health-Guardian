# 在main_7.py的基础上修改
# 使用main函数中传入JSON格式数据，处理单个员工

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


def generate_health_tips(employee_data):
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备系统消息，包含当前时间
    system_msg = system_content.format(current_time)

    # 将员工数据转换为JSON字符串
    employee_data_str = json.dumps(employee_data, ensure_ascii=False)

    messages = [
        {
            "role": "system",
            "content": system_msg
        },
        {
            "role": "user",
            "content": f"以下是员工的健康数据，请生成相应的健康提示：\n{employee_data_str}"
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
    # 示例员工数据
    example_employee_data = {
        "name": "张三",
        "department": "技术部",
        "employee_id": "TECH001",
        "station": "A区-工位10",
        "water_cups": 5,
        "sit_start_time": "2024-06-14 09:00:00"
    }

    # 生成健康提示
    health_tips = generate_health_tips(example_employee_data)
    print("健康提示：")
    print(health_tips)
