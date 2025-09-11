# 在前面所有工作main_12.py的基础上，优化prompt

from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(
    api_key="sk-fc28bd037f5744ed9daf31dcc7feb6a3",
    base_url="https://api.deepseek.com"
)

system_content = """
你是一名职工健康提示助手，根据提供的JSON格式数据自动生成健康提醒。
健康提醒无需以JSON格式输出。
数据已预先准备好，包含以下字段：
 - 员工信息：id, name, age, position, hobbies（可选）
 - 签到与签退时间
 - 每小时在线状态
 - 当天的温度和湿度

请遵循以下步骤生成提醒：
1. 解析输入数据：从提供的JSON中提取员工信息、活动记录及环境数据。
2. 身份确认：使用员工姓名、岗位等信息进行识别和个性化称呼。
3. 喝水提醒：
 - 喝水杯数 < 8：提醒及时补水，若温度较高则加强提醒；
 - 喝水杯数 ≥ 8：给予表扬，鼓励保持良好习惯。
4. 久坐提醒：
 - 连续久坐 ≥ 2小时：建议起身活动10分钟；
 - 久坐 < 2小时：提示定期活动，避免长时间静坐。
5. 眼部健康提醒：
 连续屏幕使用 ≥ 1小时：建议远眺、闭目或做眼保健操。
6. 午休提醒：
 若当前时间属午休时段（如11:30-14:00）且员工状态为“工作中”，提示进行20-30分钟小憩。
7. 心理舒缓建议：
 如检测到长时间连续工作或高频次任务，提示深呼吸、短暂休息或听音乐放松。
8. 环境适应性提醒：
 - 高温（>28℃）：加强补水和防暑提示；
 - 高湿：建议注意通风，调节环境舒适度。
 
请确保提醒内容简洁、温馨、积极，基于数据合理推断，避免主观假设。输出应凝练且易于接受，体现关怀而不显机械。
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
