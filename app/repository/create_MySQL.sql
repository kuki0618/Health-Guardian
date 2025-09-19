CREATE TABLE employees (
    userid VARCHAR(50) PRIMARY KEY, -- Ա��ID��������
    name VARCHAR(50) NOT NULL, -- ����
    title VARCHAR(50), -- ְλ
    hobby VARCHAR(100), -- ����
    age INT, -- ����
);

TRUNCATE TABLE employees;

ALTER TABLE online_status AUTO_INCREMENT = 1;

ALTER TABLE employees ADD COLUMN unionid VARCHAR(100) NOT NULL

DROP TABLE IF EXISTS employees;

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

CREATE TABLE online_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    date DATE NOT NULL FOREIGN KEY (userid) REFERENCES employees (userid) ON DELETE CASCADE
);

ALTER TABLE online_status
ADD UNIQUE KEY unique_user_date (userid, date);

ALTER TABLE online_status AUTO_INCREMENT = 1;

ALTER TABLE online_status
ADD CONSTRAINT fk_online_status_userid FOREIGN KEY (userid) REFERENCES employees (userid) ON DELETE CASCADE;

DROP TABLE IF EXISTS online_status

CREATE TABLE online_time_periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- ��������������������ID
    start_datetime DATETIME,
    end_datetime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

TRUNCATE TABLE online_time_periods

DROP TABLE IF EXISTS online_time_periods;

CREATE TABLE health_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- ��������������������ID
    data_time DATETIME,
    msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

TRUNCATE TABLE health_message;

DROP TABLE IF EXISTS health_message;

CREATE TABLE attendance_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- ��������������������ID
    userCheckTime VARCHAR(255) NOT NULL,
    checkType VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

TRUNCATE TABLE attendance_data;

DROP TABLE IF EXISTS attendance_data;

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