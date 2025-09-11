# Python ʹ��ͬ��Repository��ʾ������

## ��װ�͵���

```python
import clr
import sys

# ���.NET����·��
sys.path.append(r"path\to\your\RepositoriesCore.dll")

# ����.NET����
clr.AddReference("RepositoriesCore")

# ���������ռ�
from RepositoriesCore import RepositoriesFactory
from System.Collections.Generic import Dictionary
from System import String, Object, DateTime, Boolean
```

## ����ʹ��

### 1. ����Repositoryʵ��

```python
# ���ݿ������ַ���
connection_string = "Server=localhost;Database=test;Uid=root;Pwd=password;"

# ������ͬ���͵�Repository
employees_repo = RepositoriesFactory.CreateEmployeesSyncRepository(connection_string)
activity_logs_repo = RepositoriesFactory.CreateActivityLogsSyncRepository(connection_string)
recommendations_repo = RepositoriesFactory.CreateRecommendationsSyncRepository(connection_string)

# ����ʹ��ͨ�ù�������
employees_repo_alt = RepositoriesFactory.CreateSyncRepository("employees", connection_string)
```

### 2. ��ʼ�����ݿ�

```python
# ��ʼ�����ݿ��ṹ
if not employees_repo.DatabaseIsInitialized():
    success = employees_repo.InitializeDatabase()
    print(f"Database initialized: {success}")
```

### 3. ��Ӽ�¼

```python
# ����Ա����¼
employee_dict = Dictionary[String, Object]()
employee_dict["UUID"] = "emp-001"
employee_dict["UserId"] = "USER001"
employee_dict["Name"] = "����"
employee_dict["Department"] = "IT����"
employee_dict["WorkstationId"] = "W001"
employee_dict["Online"] = True
employee_dict["CreatedAt"] = DateTime.Now
employee_dict["UpdatedAt"] = DateTime.Now

# ��Ӽ�¼
records = clr.Convert([employee_dict], clr.GetClrType(clr.GetClrType(Dictionary[String, Object]).MakeArrayType()))
success = employees_repo.AddNewRecords(records)
print(f"Employee added: {success}")
```

### 4. ������¼

```python
# �����û�ID����Ա��
user_id = "USER001"
employees = employees_repo.GetEmployeesByUserId(user_id)

if employees:
    for emp in employees:
        print(f"Employee: {emp['Name']} - {emp['Department']}")

# ��������Ա��
online_employees = employees_repo.GetOnlineEmployees()
if online_employees:
    print(f"Found {len(online_employees)} online employees")
```

### 5. ���¼�¼

```python
# ����Ա����Ϣ
update_dict = Dictionary[String, Object]()
update_dict["Online"] = False
update_dict["UpdatedAt"] = DateTime.Now

success = employees_repo.UpdateRecord("emp-001", update_dict)
print(f"Employee updated: {success}")
```

### 6. ���־����

```python
# ��ӻ��־
activity_dict = Dictionary[String, Object]()
activity_dict["UUID"] = "activity-001"
activity_dict["UserId"] = "USER001"
activity_dict["UserUUID"] = "emp-001"
activity_dict["ActivityType"] = "����"
activity_dict["DetailInformation"] = "{\"task\": \"���\"}"
activity_dict["StartTime"] = DateTime.Now.AddHours(-2)
activity_dict["EndTime"] = DateTime.Now
activity_dict["Duration"] = 7200  # 2Сʱ
activity_dict["CreatedAt"] = DateTime.Now

activity_records = clr.Convert([activity_dict], clr.GetClrType(clr.GetClrType(Dictionary[String, Object]).MakeArrayType()))
success = activity_logs_repo.AddNewRecords(activity_records)

# �����û�ID��ȡ���־
activities = activity_logs_repo.GetActivityLogsByUserId("USER001")
if activities:
    for activity in activities:
        print(f"Activity: {activity['ActivityType']} - Duration: {activity['Duration']}s")

# ��ȡָ�����ڷ�Χ�ڵĻ
start_date = DateTime.Now.AddDays(-7)
end_date = DateTime.Now
date_range_activities = activity_logs_repo.GetActivityLogsInDateRange("USER001", start_date, end_date)
```

### 7. �Ƽ�����

```python
# ����Ƽ�
recommendation_dict = Dictionary[String, Object]()
recommendation_dict["UUID"] = "rec-001"
recommendation_dict["UserId"] = "USER001"
recommendation_dict["UserUUID"] = "emp-001"
recommendation_dict["CreateTime"] = DateTime.Now
recommendation_dict["IsPushed"] = False
recommendation_dict["Content"] = "�������Ϣ"

rec_records = clr.Convert([recommendation_dict], clr.GetClrType(clr.GetClrType(Dictionary[String, Object]).MakeArrayType()))
success = recommendations_repo.AddNewRecords(rec_records)

# ��ȡδ���͵��Ƽ�
unpushed = recommendations_repo.GetUnpushedRecommendations()
if unpushed:
    print(f"Found {len(unpushed)} unpushed recommendations")

# ����Ƽ�Ϊ������
success = recommendations_repo.MarkRecommendationAsPushed("rec-001")
print(f"Recommendation marked as pushed: {success}")
```

## ������

```python
try:
    # Repository����
    success = employees_repo.AddNewRecords(records)
    if not success:
        print("Failed to add records")
except Exception as e:
    print(f"Error: {str(e)}")
```

## ע������

1. **��������ת��**: 
   - ��Python�д���Dictionaryʱ����Ҫָ����������
   - ����ʹ�� `DateTime.Now` �� `DateTime(year, month, day, hour, minute, second)`
   - ����ֵʹ�� `True`/`False`

2. **����ת��**:
   - ʹ�� `clr.Convert()` ��Python�б�ת��Ϊ.NET����

3. **�����ַ���**:
   - ȷ�����ݿ������ַ�����ʽ��ȷ
   - �������б�Ҫ�����Ӳ���

4. **������**:
   - ���з�����������ȷ�ĳɹ�/ʧ��״̬
   - ʹ��try-catch�����쳣

5. **���ܿ���**:
   - ͬ�������������̣߳��ʺϼ򵥵Ľű�ʹ��
   - ���ڸ߲�������������ʹ��ԭʼ���첽�汾