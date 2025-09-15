# 从get_employee_data函数中获取多个员工信息
# 传入数据方式：修改get_employee_data函数中的内容

from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(
    api_key="Your-api-key-here",
    base_url="https://api.deepseek.com"
)

system_content = """
你是一名职工健康提示助手，根据提供的JSON格式数据对员工进行健康提醒。
健康提醒无需以JSON格式输出。
JSON数据已预先准备好，包含以下字段(以下为示例，提示时请以实际数据为准)：
{{
  "employee_info":
  {{
    "name": "pkx",
    "ID":1111,
    "age": 20,
    "workspace": "A115",
    "position": "研发部",
    "hobbies":"音乐"
  }},
  "check_in_out":
  {{
    "09:00 a.m.": "离开",
    "10:00 a.m.": "离开",
    "11:00 a.m.": "离开",
    "12:00 a.m.": "离开",
    "13:00 p.m.": "离开",
    "14:00 p.m.": "离开",
    "15:00 p.m.": "离开",
    "16:00 p.m.": "离开",
    "17:00 p.m.": "离开"
  }},
  "weather":
  {{
    "temperature": 26
  }}
}}

请遵循以下步骤生成提醒：
1. 解析数据：从提供的JSON中提取员工信息、活动记录及环境数据。
2. 身份确认：使用员工ID、姓名、岗位、工位等信息进行识别和个性化称呼。
3. 久坐、喝水、眼部健康提醒：
 - 如果员连续两个小时都是在线状态，则建议员工起身活动活动走一走，避免久坐，深呼吸，眺望远处或者闭目养神，放松眼睛，短暂休息。
 - 如果当日温度高于28℃，且当前时间为下午，则同时提醒员工喝水，注意及时补水。
4. 午休提醒：
 若当前时间属午休时段（如11:30-14:00）且员工状态为“在线”，提示进行20-30分钟小憩。
5. 环境适应性提醒：
 - 高温（>28℃）：加强补水和防暑提示；
 - 高湿：建议注意通风，调节环境舒适度。

请确保提醒内容简洁、温馨、积极，基于数据合理推断，避免主观假设。
输出应凝练且易于接受，体现关怀而不显机械。
当前时间：{current_time}
"""


def generate_health_tips(employee_data):
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备系统消息，包含当前时间
    system_msg = system_content.format(current_time=current_time)

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


# 传入员工数据
def get_employee_data():
    employee_data = [
        {
            "employee_info": {
                "name": "张三",
                "ID": 1001,
                "age": 28,
                "workspace": "A101",
                "position": "技术部",
                "hobbies": "篮球,阅读"
            },
            "check_in_out": {
                "09:00 a.m.": "在线",
                "10:00 a.m.": "在线",
                "11:00 a.m.": "在线",
                "12:00 p.m.": "离开",
                "13:00 p.m.": "在线",
                "14:00 p.m.": "在线",
                "15:00 p.m.": "在线",
                "16:00 p.m.": "离开",
                "17:00 p.m.": "在线"
            },
            "weather": {
                "temperature": 32
            }
        },
        {
            "employee_info": {
                "name": "李四",
                "ID": 1002,
                "age": 32,
                "workspace": "B205",
                "position": "市场部",
                "hobbies": "摄影,旅行"
            },
            "check_in_out": {
                "09:00 a.m.": "在线",
                "10:00 a.m.": "离开",
                "11:00 a.m.": "在线",
                "12:00 p.m.": "离开",
                "13:00 p.m.": "在线",
                "14:00 p.m.": "离开",
                "15:00 p.m.": "在线",
                "16:00 p.m.": "在线",
                "17:00 p.m.": "在线"
            },
            "weather": {
                "temperature": 29
            }
        },
        {
            "employee_info": {
                "name": "王五",
                "ID": 1003,
                "age": 25,
                "workspace": "C312",
                "position": "设计部",
                "hobbies": "绘画,音乐"
            },
            "check_in_out": {
                "09:00 a.m.": "离开",
                "10:00 a.m.": "在线",
                "11:00 a.m.": "在线",
                "12:00 p.m.": "在线",
                "13:00 p.m.": "离开",
                "14:00 p.m.": "在线",
                "15:00 p.m.": "在线",
                "16:00 p.m.": "在线",
                "17:00 p.m.": "离开"
            },
            "weather": {
                "temperature": 26
            }
        }
    ]
    return employee_data


if __name__ == "__main__":
    # 示例员工数据
    example_employee_data = get_employee_data()

    # 生成健康提示
    health_tips = generate_health_tips(example_employee_data)
    print("健康提示：")
    print(health_tips)


# 输出结果：
# 健康提示：
# 张三（技术部/A101），注意到您从9点到11点连续在线工作，建议起身活动一下，深呼吸或远眺放松眼睛。今日气温较高（32℃），请多喝水防暑降温哦！

# 李四（市场部/B205），您下午3点至5点持续在岗，记得适当起身走动，避免久坐。今天温度29℃，午后炎热，请及时补水，保持水分充足～

# 王五（设计部/C312），您下午2点到4点连续工作未休息，建议短暂活动放松肩颈，眺望远处缓解眼部疲劳。温度适中，保持通风更舒适！
