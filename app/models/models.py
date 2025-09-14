# ��get_employee_data�����л�ȡ���Ա����Ϣ
# �������ݷ�ʽ���޸�get_employee_data�����е�����

from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(
    api_key="Your-api-key-here",
    base_url="https://api.deepseek.com"
)

system_content = """
����һ��ְ��������ʾ���֣������ṩ��JSON��ʽ���ݶ�Ա�����н������ѡ�
��������������JSON��ʽ�����
JSON������Ԥ��׼���ã����������ֶ�(����Ϊʾ������ʾʱ����ʵ������Ϊ׼)��
{{
  "employee_info":
  {{
    "name": "pkx",
    "ID":1111,
    "age": 20,
    "workspace": "A115",
    "position": "�з���",
    "hobbies":"����"
  }},
  "check_in_out":
  {{
    "09:00 a.m.": "�뿪",
    "10:00 a.m.": "�뿪",
    "11:00 a.m.": "�뿪",
    "12:00 a.m.": "�뿪",
    "13:00 p.m.": "�뿪",
    "14:00 p.m.": "�뿪",
    "15:00 p.m.": "�뿪",
    "16:00 p.m.": "�뿪",
    "17:00 p.m.": "�뿪"
  }},
  "weather":
  {{
    "temperature": 26
  }}
}}

����ѭ���²����������ѣ�
1. �������ݣ����ṩ��JSON����ȡԱ����Ϣ�����¼���������ݡ�
2. ���ȷ�ϣ�ʹ��Ա��ID����������λ����λ����Ϣ����ʶ��͸��Ի��ƺ���
3. ��������ˮ���۲��������ѣ�
 - ���Ա��������Сʱ��������״̬������Ա���������һ�ߣ���������������������Զ�����߱�Ŀ���񣬷����۾���������Ϣ��
 - ��������¶ȸ���28�棬�ҵ�ǰʱ��Ϊ���磬��ͬʱ����Ա����ˮ��ע�⼰ʱ��ˮ��
4. �������ѣ�
 ����ǰʱ��������ʱ�Σ���11:30-14:00����Ա��״̬Ϊ�����ߡ�����ʾ����20-30����С��
5. ������Ӧ�����ѣ�
 - ���£�>28�棩����ǿ��ˮ�ͷ�����ʾ��
 - ��ʪ������ע��ͨ�磬���ڻ������ʶȡ�

��ȷ���������ݼ�ࡢ��ܰ���������������ݺ����ƶϣ��������ۼ��衣
���Ӧ���������ڽ��ܣ����ֹػ������Ի�е��
��ǰʱ�䣺{current_time}
"""


def generate_health_tips(employee_data):
    # ��ȡ��ǰʱ��
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ׼��ϵͳ��Ϣ��������ǰʱ��
    system_msg = system_content.format(current_time=current_time)

    # ��Ա������ת��ΪJSON�ַ���
    employee_data_str = json.dumps(employee_data, ensure_ascii=False)

    messages = [
        {
            "role": "system",
            "content": system_msg
        },
        {
            "role": "user",
            "content": f"������Ա���Ľ������ݣ���������Ӧ�Ľ�����ʾ��\n{employee_data_str}"
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
        return f"����APIʱ���ִ���: {e}"


# ����Ա������
def get_employee_data():
    employee_data = [
        {
            "employee_info": {
                "name": "����",
                "ID": 1001,
                "age": 28,
                "workspace": "A101",
                "position": "������",
                "hobbies": "����,�Ķ�"
            },
            "check_in_out": {
                "09:00 a.m.": "����",
                "10:00 a.m.": "����",
                "11:00 a.m.": "����",
                "12:00 p.m.": "�뿪",
                "13:00 p.m.": "����",
                "14:00 p.m.": "����",
                "15:00 p.m.": "����",
                "16:00 p.m.": "�뿪",
                "17:00 p.m.": "����"
            },
            "weather": {
                "temperature": 32
            }
        },
        {
            "employee_info": {
                "name": "����",
                "ID": 1002,
                "age": 32,
                "workspace": "B205",
                "position": "�г���",
                "hobbies": "��Ӱ,����"
            },
            "check_in_out": {
                "09:00 a.m.": "����",
                "10:00 a.m.": "�뿪",
                "11:00 a.m.": "����",
                "12:00 p.m.": "�뿪",
                "13:00 p.m.": "����",
                "14:00 p.m.": "�뿪",
                "15:00 p.m.": "����",
                "16:00 p.m.": "����",
                "17:00 p.m.": "����"
            },
            "weather": {
                "temperature": 29
            }
        },
        {
            "employee_info": {
                "name": "����",
                "ID": 1003,
                "age": 25,
                "workspace": "C312",
                "position": "��Ʋ�",
                "hobbies": "�滭,����"
            },
            "check_in_out": {
                "09:00 a.m.": "�뿪",
                "10:00 a.m.": "����",
                "11:00 a.m.": "����",
                "12:00 p.m.": "����",
                "13:00 p.m.": "�뿪",
                "14:00 p.m.": "����",
                "15:00 p.m.": "����",
                "16:00 p.m.": "����",
                "17:00 p.m.": "�뿪"
            },
            "weather": {
                "temperature": 26
            }
        }
    ]
    return employee_data


if __name__ == "__main__":
    # ʾ��Ա������
    example_employee_data = get_employee_data()

    # ���ɽ�����ʾ
    health_tips = generate_health_tips(example_employee_data)
    print("������ʾ��")
    print(health_tips)


# ��������
# ������ʾ��
# ������������/A101����ע�⵽����9�㵽11���������߹�������������һ�£��������Զ�������۾����������½ϸߣ�32�棩������ˮ�����Ŷ��

# ���ģ��г���/B205����������3����5������ڸڣ��ǵ��ʵ������߶�����������������¶�29�棬������ȣ��뼰ʱ��ˮ������ˮ�ֳ��㡫

# ���壨��Ʋ�/C312����������2�㵽4����������δ��Ϣ��������ݻ���ɼ羱������Զ�������۲�ƣ�͡��¶����У�����ͨ������ʣ�
