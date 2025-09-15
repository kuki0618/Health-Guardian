import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek


# 解析工作状态数据
def parse_work_status(work_status):
    parsed_data = {}
    for day, hours in work_status.items():
        if day == "seventh":  # 第七天是休息
            parsed_data[day] = {"status": "休息"}
            continue

        parsed_hours = {}
        for hour, info in hours.items():
            parsed_hours[int(hour)] = {
                "status": info["status"],
                "steps": info["steps"]
            }
        parsed_data[day] = parsed_hours
    return parsed_data


# 全局员工数据
employee_data = {
    "employee_info": {
        "name": "张三",
        "extension": {
            "爱好": "篮球",
            "年龄": "24"
        },
        "title": "算法工程师"
    },
    "work_status": {
        "first": {
            "08": {"status": "签到", "steps": 3000},
            "09": {"status": "离开", "steps": 2500},
            "10": {"status": "在线", "steps": 3000},
            "11": {"status": "在线", "steps": 4500},
            "12": {"status": "离开", "steps": 6000},
            "13": {"status": "在线", "steps": 6500},
            "14": {"status": "在线", "steps": 7000},
            "15": {"status": "会议", "steps": 7200},
            "16": {"status": "在线", "steps": 7500},
            "17": {"status": "在线", "steps": 8500},
            "18": {"status": "离开", "steps": 9000},
            "20": {"status": "在线", "steps": 10000}
        },
        "second": {
            "08": {"status": "签到", "steps": 2800},
            "09": {"status": "在线", "steps": 3200},
            "10": {"status": "在线", "steps": 3500},
            "11": {"status": "会议", "steps": 3800},
            "12": {"status": "离开", "steps": 5200},
            "13": {"status": "在线", "steps": 5500},
            "14": {"status": "在线", "steps": 6000},
            "15": {"status": "离开", "steps": 6200},
            "16": {"status": "在线", "steps": 6500},
            "17": {"status": "在线", "steps": 7800},
            "18": {"status": "签退", "steps": 8200}
        },
        "third": {
            "08": {"status": "签到", "steps": 3100},
            "09": {"status": "在线", "steps": 3400},
            "10": {"status": "在线", "steps": 3800},
            "11": {"status": "在线", "steps": 4200},
            "12": {"status": "离开", "steps": 5800},
            "13": {"status": "在线", "steps": 6100},
            "14": {"status": "会议", "steps": 6300},
            "15": {"status": "在线", "steps": 6600},
            "16": {"status": "在线", "steps": 7200},
            "17": {"status": "在线", "steps": 8500},
            "18": {"status": "签退", "steps": 9000}
        },
        "fourth": {
            "08": {"status": "签到", "steps": 2900},
            "09": {"status": "在线", "steps": 3300},
            "10": {"status": "离开", "steps": 3500},
            "11": {"status": "在线", "steps": 3900},
            "12": {"status": "离开", "steps": 5300},
            "13": {"status": "在线", "steps": 5600},
            "14": {"status": "在线", "steps": 6200},
            "15": {"status": "在线", "steps": 6800},
            "16": {"status": "会议", "steps": 7000},
            "17": {"status": "在线", "steps": 8300},
            "18": {"status": "签退", "steps": 8700}
        },
        "fifth": {
            "08": {"status": "签到", "steps": 3200},
            "09": {"status": "在线", "steps": 3600},
            "10": {"status": "在线", "steps": 4000},
            "11": {"status": "会议", "steps": 4300},
            "12": {"status": "离开", "steps": 5900},
            "13": {"status": "在线", "steps": 6200},
            "14": {"status": "在线", "steps": 6700},
            "15": {"status": "在线", "steps": 7300},
            "16": {"status": "在线", "steps": 8000},
            "17": {"status": "在线", "steps": 9200},
            "18": {"status": "签退", "steps": 9600}
        },
        "sixth": {
            "09": {"status": "签到", "steps": 2500},
            "10": {"status": "在线", "steps": 2800},
            "11": {"status": "在线", "steps": 3200},
            "12": {"status": "离开", "steps": 4500},
            "13": {"status": "在线", "steps": 4800},
            "14": {"status": "在线", "steps": 5300},
            "15": {"status": "签退", "steps": 5600}
        },
        "seventh": {
            "status": "休息"
        }
    },
    "weather": {
        "Monday": {"temperature": 26, "condition": "晴朗"},
        "Tuesday": {"temperature": 24, "condition": "多云"},
        "Wednesday": {"temperature": 28, "condition": "晴朗"},
        "Thursday": {"temperature": 25, "condition": "小雨"},
        "Friday": {"temperature": 23, "condition": "阴天"},
        "Saturday": {"temperature": 22, "condition": "多云"},
        "Sunday": {"temperature": 20, "condition": "小雨"}
    }
}


# 工具函数：获取员工工作状态数据（使用全局数据）
def get_work_status(_):
    return parse_work_status(employee_data["work_status"])


# 工具函数：获取天气数据（使用全局数据）
def get_weather_data(_):
    return employee_data["weather"]


# 工具函数：获取员工基本信息（使用全局数据）
def get_employee_info(_):
    return employee_data["employee_info"]


# 获取当前时间
def get_current_time(_):
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# 加载环境变量
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# 初始化DeepSeek LLM
llm = ChatDeepSeek(model="deepseek-chat", api_key=deepseek_api_key)

# 定义工具（使用lambda忽略输入参数，直接调用函数）
tools = [
    Tool(
        name="GetWorkStatus",
        func=get_work_status,
        description="获取员工一周内每天各时段的工作状态数据，包括在线、离开、会议、签到、签退等状态和步数信息"
    ),
    Tool(
        name="GetWeatherData",
        func=get_weather_data,
        description="获取一周内每天的天气数据，包括温度和天气状况"
    ),
    Tool(
        name="GetEmployeeInfo",
        func=get_employee_info,
        description="获取员工的基本信息，包括姓名、职位和个人爱好等"
    ),
    Tool(
        name="GetCurrentTime",
        func=get_current_time,
        description="获取当前的日期和时间，格式为YYYY-MM-DD HH:MM"
    )
]

# 定义提示模板（匹配结构化聊天代理的预期变量）
prompt_template = """你是一个员工健康管理助手，需要根据提供的员工工作状态数据、天气数据和当前时间，按照以下规则向员工发送提醒：

1. 久坐提醒：如果员连续两个小时都是在线状态，则建议员工起身活动活动走一走，避免久坐，深呼吸，眺望远处或者闭目养神，放松眼睛，短暂休息。
2. 喝水提醒：如果当日温度高于28℃，且当前时间为下午，则同时提醒员工喝水，注意及时补水。
3. 午休提醒：若当前时间属午休时段（如11:30-14:00）且员工状态为“在线”，提示进行20-30分钟小憩。
4. 日均连续工作时长：若一周内多数天连续在线时长接近或超过3-4小时，且当前时间处于工作时段内，发送提醒
5. 夜间/凌晨工作频率：如果一周里有不少天数在晚上22:00后还在线，且当前时间为晚上时，发送提醒
6. 休息与早起工作情况：若存在前一天很晚还工作，次日清晨（当前时间）很早又在线的情况，发送提醒
7. 规律性休息情况：要是一周内工作日几乎都没有短暂"不在线"的休息时段，且当前时间处于工作时段内，发送提醒

请根据获取到的员工{employee_name}的工作状态数据、天气数据和当前时间{current_time}，分析并判断需要发送哪些提醒。请直接给出提醒内容，不需要解释分析过程。

可用工具:
{tools}

如果已经获取了足够的信息，请直接生成提醒内容。如果需要更多信息，请使用工具获取。

思考过程:
1. 首先获取当前时间、员工的工作状态数据和天气数据
2. 根据当前时间判断所处时段和对应的日期
3. 逐一检查各项提醒规则是否满足当前时间条件，结合每个员工的具体信息，生成个性化的提醒：
 - 比如员工的具体岗位是产品经理，或者HR，或者算法工程师，考虑到员工的身份，根据特定的职业输出特定的提醒。
 - 结合员工的年龄、兴趣爱好信息，进行个性化提醒。
4. 汇总所有需要发送的提醒

{agent_scratchpad}
"""

# 创建提示（使用代理所需的标准变量）
prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["tools", "agent_scratchpad", "input"]
)

# 初始化Agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt
)

# 准备输入信息
employee_name = employee_data["employee_info"]["name"]
current_time = get_current_time(None)
input_text = f"请根据当前时间{current_time}、员工{employee_name}的工作和天气数据，判断并生成即时健康提醒"

# 运行Agent
reminders = agent.invoke(input_text)

print(f"[{current_time}] 需要发送的提醒：")
print(reminders["output"])
