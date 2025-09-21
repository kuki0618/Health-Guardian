from datetime import datetime, timedelta

# 将字符串转换为datetime对象
def change_time_format(time_str1:str,time_str2:str):
    def parse_iso_time(time_str):
        if time_str is None:
            return None
        # 移除时区信息
        if '+' in time_str:
            time_str = time_str.split('+')[0]
        elif 'Z' in time_str:
            time_str = time_str.replace('Z', '')
        
        # 替换 T 为空格
        if 'T' in time_str:
            time_str = time_str.replace('T', ' ')
        
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    
    time1 = parse_iso_time(time_str1)
    time2 = parse_iso_time(time_str2)
    
    if time1 and time2:
        time_difference = time2 - time1
        return time_difference.total_seconds()
    else:
        return 0

#获取标准格式的当前时间
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#获取标准格式的当前日期
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

