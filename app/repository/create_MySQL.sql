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