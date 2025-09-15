from datetime import datetime, timedelta

# 定义时间字符串
time_str1 = "2023-10-28 9:00:00"
time_str2 = "2023-10-28 11:00:00"  # 示例中的第二个时间

# 将字符串转换为datetime对象
def change_time_format(time_str1:str,time_str2:str):
    time_format = "%Y-%m-%d %H:%M:%S"
    time1 = datetime.strptime(time_str1, time_format)
    time2 = datetime.strptime(time_str2, time_format)
    time_difference = time2 - time1
    return time_difference.total_seconds() 

