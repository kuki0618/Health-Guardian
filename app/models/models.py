import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek


# ��������״̬����
def parse_work_status(work_status):
    parsed_data = {}
    for day, hours in work_status.items():
        if day == "seventh":  # ����������Ϣ
            parsed_data[day] = {"status": "��Ϣ"}
            continue

        parsed_hours = {}
        for hour, info in hours.items():
            parsed_hours[int(hour)] = {
                "status": info["status"],
                "steps": info["steps"]
            }
        parsed_data[day] = parsed_hours
    return parsed_data

def create_message(employee_data:dict):
    # ȫ��Ա������
    '''
    employee_data = {
        "employee_info": {
            "name": "����",
            "extension": {
                "����": "����",
                "����": "24"
            },
            "title": "�㷨����ʦ"
        },
        "work_status": {
            "first": {
                "08": {"status": "ǩ��", "steps": 3000},
                "09": {"status": "�뿪", "steps": 2500},
                "10": {"status": "����", "steps": 3000},
                "11": {"status": "����", "steps": 4500},
                "12": {"status": "�뿪", "steps": 6000},
                "13": {"status": "����", "steps": 6500},
                "14": {"status": "����", "steps": 7000},
                "15": {"status": "����", "steps": 7200},
                "16": {"status": "����", "steps": 7500},
                "17": {"status": "����", "steps": 8500},
                "18": {"status": "�뿪", "steps": 9000},
                "20": {"status": "����", "steps": 10000}
            },
            "second": {
                "08": {"status": "ǩ��", "steps": 2800},
                "09": {"status": "����", "steps": 3200},
                "10": {"status": "����", "steps": 3500},
                "11": {"status": "����", "steps": 3800},
                "12": {"status": "�뿪", "steps": 5200},
                "13": {"status": "����", "steps": 5500},
                "14": {"status": "����", "steps": 6000},
                "15": {"status": "�뿪", "steps": 6200},
                "16": {"status": "����", "steps": 6500},
                "17": {"status": "����", "steps": 7800},
                "18": {"status": "ǩ��", "steps": 8200}
            },
            "third": {
                "08": {"status": "ǩ��", "steps": 3100},
                "09": {"status": "����", "steps": 3400},
                "10": {"status": "����", "steps": 3800},
                "11": {"status": "����", "steps": 4200},
                "12": {"status": "�뿪", "steps": 5800},
                "13": {"status": "����", "steps": 6100},
                "14": {"status": "����", "steps": 6300},
                "15": {"status": "����", "steps": 6600},
                "16": {"status": "����", "steps": 7200},
                "17": {"status": "����", "steps": 8500},
                "18": {"status": "ǩ��", "steps": 9000}
            },
            "fourth": {
                "08": {"status": "ǩ��", "steps": 2900},
                "09": {"status": "����", "steps": 3300},
                "10": {"status": "�뿪", "steps": 3500},
                "11": {"status": "����", "steps": 3900},
                "12": {"status": "�뿪", "steps": 5300},
                "13": {"status": "����", "steps": 5600},
                "14": {"status": "����", "steps": 6200},
                "15": {"status": "����", "steps": 6800},
                "16": {"status": "����", "steps": 7000},
                "17": {"status": "����", "steps": 8300},
                "18": {"status": "ǩ��", "steps": 8700}
            },
            "fifth": {
                "08": {"status": "ǩ��", "steps": 3200},
                "09": {"status": "����", "steps": 3600},
                "10": {"status": "����", "steps": 4000},
                "11": {"status": "����", "steps": 4300},
                "12": {"status": "�뿪", "steps": 5900},
                "13": {"status": "����", "steps": 6200},
                "14": {"status": "����", "steps": 6700},
                "15": {"status": "����", "steps": 7300},
                "16": {"status": "����", "steps": 8000},
                "17": {"status": "����", "steps": 9200},
                "18": {"status": "ǩ��", "steps": 9600}
            },
            "sixth": {
                "09": {"status": "ǩ��", "steps": 2500},
                "10": {"status": "����", "steps": 2800},
                "11": {"status": "����", "steps": 3200},
                "12": {"status": "�뿪", "steps": 4500},
                "13": {"status": "����", "steps": 4800},
                "14": {"status": "����", "steps": 5300},
                "15": {"status": "ǩ��", "steps": 5600}
            },
            "seventh": {
                "status": "��Ϣ"
            }
        },
        "weather": {
            "Monday": {"temperature": 26, "condition": "����"},
            "Tuesday": {"temperature": 24, "condition": "����"},
            "Wednesday": {"temperature": 28, "condition": "����"},
            "Thursday": {"temperature": 25, "condition": "С��"},
            "Friday": {"temperature": 23, "condition": "����"},
            "Saturday": {"temperature": 22, "condition": "����"},
            "Sunday": {"temperature": 20, "condition": "С��"}
        }
    }
    '''


    # ���ߺ�������ȡԱ������״̬���ݣ�ʹ��ȫ�����ݣ�
    def get_work_status(_):
        return parse_work_status(employee_data["work_status"])


    # ���ߺ�������ȡ�������ݣ�ʹ��ȫ�����ݣ�
    def get_weather_data(_):
        return employee_data["weather"]


    # ���ߺ�������ȡԱ��������Ϣ��ʹ��ȫ�����ݣ�
    def get_employee_info(_):
        return employee_data["employee_info"]


    # ��ȡ��ǰʱ��
    def get_current_time(_):
        return datetime.now().strftime("%Y-%m-%d %H:%M")


    # ���ػ�������
    load_dotenv()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

    # ��ʼ��DeepSeek LLM
    llm = ChatDeepSeek(model="deepseek-chat", api_key=deepseek_api_key)

    # ���幤�ߣ�ʹ��lambda�������������ֱ�ӵ��ú�����
    tools = [
        Tool(
            name="GetWorkStatus",
            func=get_work_status,
            description="��ȡԱ��һ����ÿ���ʱ�εĹ���״̬���ݣ��������ߡ��뿪�����顢ǩ����ǩ�˵�״̬�Ͳ�����Ϣ"
        ),
        Tool(
            name="GetWeatherData",
            func=get_weather_data,
            description="��ȡ������������ݣ������¶Ⱥ�����״��"
        ),
        Tool(
            name="GetEmployeeInfo",
            func=get_employee_info,
            description="��ȡԱ���Ļ�����Ϣ������������ְλ�͸��˰��õ�"
        ),
        Tool(
            name="GetCurrentTime",
            func=get_current_time,
            description="��ȡ��ǰ�����ں�ʱ�䣬��ʽΪYYYY-MM-DD HH:MM"
        )
    ]

    # ������ʾģ�壨ƥ��ṹ����������Ԥ�ڱ�����
    prompt_template = """����һ��Ա�������������֣���Ҫ�����ṩ��Ա������״̬���ݡ��������ݺ͵�ǰʱ�䣬�������¹�����Ա���������ѣ�

    1. �������ѣ����Ա��������Сʱ��������״̬������Ա���������һ�ߣ���������������������Զ�����߱�Ŀ���񣬷����۾���������Ϣ��
    2. ��ˮ���ѣ���������¶ȸ���28�棬�ҵ�ǰʱ��Ϊ���磬��ͬʱ����Ա����ˮ��ע�⼰ʱ��ˮ��
    3. �������ѣ�����ǰʱ��������ʱ�Σ���11:30-14:00����Ա��״̬Ϊ�����ߡ�����ʾ����20-30����С��
    4. �վ���������ʱ������һ���ڶ�������������ʱ���ӽ��򳬹�3-4Сʱ���ҵ�ǰʱ�䴦�ڹ���ʱ���ڣ���������
    5. ҹ��/�賿����Ƶ�ʣ����һ�����в�������������22:00�����ߣ��ҵ�ǰʱ��Ϊ����ʱ����������
    6. ��Ϣ�������������������ǰһ����������������峿����ǰʱ�䣩���������ߵ��������������
    7. ��������Ϣ�����Ҫ��һ���ڹ����ռ�����û�ж���"������"����Ϣʱ�Σ��ҵ�ǰʱ�䴦�ڹ���ʱ���ڣ���������

    ����ݻ�ȡ����Ա��{employee_name}�Ĺ���״̬���ݡ��������ݺ͵�ǰʱ��{current_time}���������ж���Ҫ������Щ���ѡ���ֱ�Ӹ����������ݣ�����Ҫ���ͷ������̡�

    ���ù���:
    {tools}

    ����Ѿ���ȡ���㹻����Ϣ����ֱ�������������ݡ������Ҫ������Ϣ����ʹ�ù��߻�ȡ��

    ˼������:
    1. ���Ȼ�ȡ��ǰʱ�䡢Ա���Ĺ���״̬���ݺ���������
    2. ���ݵ�ǰʱ���ж�����ʱ�κͶ�Ӧ������
    3. ��һ���������ѹ����Ƿ����㵱ǰʱ�����������ÿ��Ա���ľ�����Ϣ�����ɸ��Ի������ѣ�
    - ����Ա���ľ����λ�ǲ�Ʒ��������HR�������㷨����ʦ�����ǵ�Ա������ݣ������ض���ְҵ����ض������ѡ�
    - ���Ա�������䡢��Ȥ������Ϣ�����и��Ի����ѡ�
    4. ����������Ҫ���͵�����

    {agent_scratchpad}
    """

    # ������ʾ��ʹ�ô�������ı�׼������
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["tools", "agent_scratchpad", "input"]
    )

    # ��ʼ��Agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prompt=prompt
    )

    # ׼��������Ϣ
    employee_name = employee_data["employee_info"]["name"]
    current_time = get_current_time(None)
    input_text = f"����ݵ�ǰʱ��{current_time}��Ա��{employee_name}�Ĺ������������ݣ��жϲ����ɼ�ʱ��������"

    # ����Agent
    reminders = agent.invoke(input_text)

    print(f"[{current_time}] ��Ҫ���͵����ѣ�")
    return reminders["output"]