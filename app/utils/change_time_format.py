from datetime import datetime, timedelta

# ����ʱ���ַ���
time_str1 = "2023-10-28 9:00:00"
time_str2 = "2023-10-28 11:00:00"  # ʾ���еĵڶ���ʱ��

# ���ַ���ת��Ϊdatetime����
def change_time_format(time_str1:str,time_str2:str):
    time_format = "%Y-%m-%d %H:%M:%S"
    time1 = datetime.strptime(time_str1, time_format)
    time2 = datetime.strptime(time_str2, time_format)
    time_difference = time2 - time1
    return time_difference.total_seconds() 

