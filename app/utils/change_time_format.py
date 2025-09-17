from datetime import datetime, timedelta

# 将字符串转换为datetime对象
def change_time_format(time_str1:str,time_str2:str):
    time_format = "%Y-%m-%d %H:%M:%S"
    time1 = datetime.strptime(time_str1, time_format)
    time2 = datetime.strptime(time_str2, time_format)
    time_difference = time2 - time1
    return time_difference.total_seconds() 

#获取标准格式的当前时间
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#获取标准格式的当前日期
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

