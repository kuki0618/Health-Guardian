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
        '������',
        '�㷨����ʦ',
        'ɢ��',
        26
    );

INSERT INTO
    employees
VALUES (
        "604157341328085868",
        '�˿���',
        '��Ʒ����',
        '��Ӿ',
        23
    );

INSERT INTO
    employees
VALUES (
        "03366627182021511253",
        '˾���',
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
    attendance_id INT NOT NULL, -- ��������������������ID
    start_datetime DATETIME,
    end_datetime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

-- �������Լ������֤����������
FOREIGN KEY (attendance_id) REFERENCES online_status(id) ON DELETE CASCADE
);

INSERT INTO
    online_status (userid, date)
VALUES ('manager4585', '2025-09-06');

-- ��ȡ�ղ��������ID������Ϊ 1����Ȼ����ʱ����ӱ������ʱ���
INSERT INTO
    online_time_periods (
        attendance_id,
        start_datetime,
        end_datetime
    )
VALUES (
        1,
        '2023-10-28 09:00:00',
        '2023-10-30 18:00:00'
    ),
    (
        1,
        '2023-10-31 09:00:00',
        '2023-11-01 18:00:00'
    ),
    (
        1,
        '2023-11-02 10:00:00',
        NULL
    );
-- ����������һ��δ������ʱ���