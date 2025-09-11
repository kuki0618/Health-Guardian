# 对main_11.py的修改
# 使用文件读入JSON数据的方式处理多个员工
# 示例文件employee_data.json

# 使用文件读入JSON数据的方式处理多个员工
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
        # 检查是否为空值
        if not sit_start_time:
            return 0

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
    try:
        # 从文件读取JSON数据的示例
        with open("employee_data.json", "r", encoding="utf-8") as f:
            employee_data = json.load(f)

            # 检查是否为多个员工的数据
            if isinstance(employee_data, list):
                for employee in employee_data:
                    health_tips = generate_health_tips(employee)
                    print(f"员工 {employee.get('name', '未知')} 的健康提示: ")
                    print(health_tips)
                    print("\n" + "=" * 50 + "\n")
            else:
                health_tips = generate_health_tips(employee_data)
                print("健康提示: ")
                print(health_tips)
                print("\n")

    except FileNotFoundError:
        print("错误：找不到 employee_data.json 文件")
    except json.JSONDecodeError:
        print("错误：employee_data.json 文件格式不正确")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")


# 最终结果输出：
# 健康提示:
# ### 员工健康提示

# #### 张三（技术部，编号TECH001，工位A区-工位10）：
# - **喝水提醒**：您今天喝了5杯水，建议及时补充水源摄入，每天至少8杯水以保持身体水分平衡哦！
# - **久坐提醒**：您从15:31开始久坐，到当前时间17:04，已连续坐了约1小时33分钟。虽然时间还不算太长，但建议每隔一段时间就起身活动一下，伸展身体，避免长时间保持同一姿势。

# #### 李四（市场部，编号MKT002，工位B区-工位5）：
# - **喝水提醒**：您今天喝了3杯水，喝水不足哦！请记得及时补充水分，每天8杯水有助于提高注意力和健康。
# - **久坐提醒**：您从09:15开始久坐，到当前时间17:04，已连续坐了约7小时49分钟。这已经超过2小时了，建议立即起身活动至少10分钟，走动一下或做些伸展，缓解肌肉疲劳。

# #### 王五（财务部，编号FIN003，工位C区-工位3）：
# - **喝水提醒**：太棒了！您今天已经喝了9杯水，超过了推荐量。继续保持这样的好习惯，这对您的健康和活力很有帮助！
# - **久坐提醒**：您从08:45开始久坐，到当前时间17:04，已连续坐了约8小时19分钟。这远超过2小时，强烈建议您起身活动一下，至少休息10分钟，走动或做简单的伸展运动，以避免久坐带来的健康风险。

# **通用建议**：
# 无论久坐时间长短，都建议每隔30-60分钟就短暂活动一下。多喝水、常活动，让工作更高效，身体更健康！ 😊
