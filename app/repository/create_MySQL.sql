CREATE TABLE employees (
    userid VARCHAR(50) PRIMARY KEY, -- Ա��ID��������
    name VARCHAR(50) NOT NULL, -- ����
    title VARCHAR(50), -- ְλ
    hobby VARCHAR(100), -- ����
    age INT -- ����
);

INSERT INTO
    employees
VALUES (
        "manager4585",
        'С��',
        '�㷨����ʦ',
        'ɢ��',
        26
    );

INSERT INTO
    employees
VALUES (
        "604157341328085868",
        'С��',
        '��Ʒ����',
        '��Ӿ',
        23
    );

INSERT INTO
    employees
VALUES (
        "03366627182021511253",
        'С�',
        '���',
        '����',
        26
    );

'''
CREATE TABLE clock_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY, -- ��ţ�����������
    date DATE NOT NULL, -- ����
    employee_id INT NOT NULL, -- Ա��ID�������
    clock_in_time DATETIME, -- ǩ��ʱ��
    clock_out_time DATETIME, -- ǩ��ʱ��
    FOREIGN KEY (employee_id) REFERENCES employees (userid)
);

INSERT INTO
    clock_records (
        date,
        employee_id,
        clock_in_time,
        clock_out_time
    )
VALUES (
        '2023-09-06',
        1552,
        '08:45:00',
        '18:45:00'
    ),
    (
        '2023-09-06',
        1553,
        '09:45:00',
        '20:45:00'
    );
'''

CREATE TABLE online_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE online_time_periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- ��������������������ID
    start_datetime DATETIME,
    end_datetime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

CREATE TABLE health_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- ��������������������ID
    data_time DATETIME,
    msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

CREATE TABLE attendance_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- ��������������������ID
    userCheckTime VARCHAR(255) NOT NULL,
    checkType VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

INSERT INTO
    online_status (userid, date)
VALUES ('manager4585', '2025-09-06');

INSERT INTO
    online_status (userid, date)
VALUES (
        '604157341328085868',
        '2025-09-06'
    );

-- ��ȡ�ղ��������ID������Ϊ 1����Ȼ����ʱ����ӱ������ʱ���
INSERT INTO
    online_time_periods (
        task_id,
        start_datetime,
        end_datetime
    )
VALUES (
        1,
        '2025-09-06 08:28:45',
        '2025-09-06 10:00:00'
    ),
    (
        1,
        '2025-09-06 11:26:38',
        '2025-09-06 12:45:58'
    ),
    (
        1,
        '2025-09-06 13:56:35',
        '2025-09-06 15:00:00'
    );

INSERT INTO
    health_message (task_id, data_time, msg)
VALUES (
        1,
        '2025-09-06 11:00:00',
        "����9�㵽11���������߹���,��������һ��,�������Զ�������۾����������½ϸ�(32��),����ˮ�����Ŷ��"
    ),
    (
        2,
        '2025-09-06 15:00:00',
        "������3����5������ڸ�,�ǵ��ʵ������߶�,��������������¶�29��,�������,�뼰ʱ��ˮ,����ˮ�ֳ��㡫"
    );

INSERT INTO
    attendance_data (
        task_id,
        userCheckTime,
        checkType
    )
VALUES (
        1,
        '2025-09-06 8:45:32',
        "OnDuty"
    ),
    (
        2,
        '2025-09-06 9:01:47',
        "OnDuty"
    );