CREATE TABLE employees (
    userid VARCHAR(50) PRIMARY KEY, -- Ա��ID��������
    name VARCHAR(50) NOT NULL, -- ����
    title VARCHAR(50), -- ְλ
    hobby VARCHAR(100), -- ����
    age INT, -- ����
);

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

ADD UNIQUE KEY unique_user_date (userid, date);

ALTER TABLE online_status AUTO_INCREMENT = 1;

ALTER TABLE online_status ADD COLUMN steps INT DEFAULT 0;

ALTER TABLE online_status
ADD CONSTRAINT fk_online_status_userid FOREIGN KEY (userid) REFERENCES employees (userid) ON DELETE CASCADE;

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
    date_time DATETIME,
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
VALUES ('manager4585', '2025-09-18'),
    ('manager4585', '2025-09-19'),
    ('manager4585', '2025-09-20'),
    ('manager4585', '2025-09-21'),
    ('manager4585', '2025-09-22');

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
        "2025-9-18 09:30:00",
        "2025-9-18 11:00:00"
    ),
    (
        1,
        "2025-9-18 13:30:00",
        "2025-9-18 14:20:00"
    ),
    (
        1,
        "2025-9-18 15:30:00",
        "2025-9-18 17:00:00"
    ),
    (
        2,
        "2025-9-19 08:30:00",
        "2025-9-19 10:40:00"
    ),
    (
        2,
        "2025-9-19 13:20:00",
        "2025-9-19 15:50:00"
    ),
    (
        2,
        "2025-9-19 17:20:00",
        "2025-9-19 19:00:00"
    ),
    (
        3,
        "2025-9-20 08:40:00",
        "2025-9-20 11:00:00"
    ),
    (
        3,
        "2025-9-20 13:00:00",
        "2025-9-20 14:30:00"
    ),
    (
        3,
        "2025-9-20 15:30:00",
        "2025-9-20 17:30:00"
    ),
    (
        3,
        "2025-9-20 18:00:00",
        "2025-9-20 19:00:00"
    ),
    (
        4,
        "2025-9-21 08:30:00",
        "2025-9-21 11:45:00"
    ),
    (
        4,
        "2025-9-21 14:00:00",
        "2025-9-21 16:30:00"
    ),
    (
        4,
        "2025-9-21 17:30:00",
        "2025-9-21 19:00:00"
    );

INSERT INTO
    attendance_data (
        task_id,
        userCheckTime,
        checkType
    )
VALUES (
        1,
        '2025-09-18 8:19:17',
        "OnDuty"
    ),
    (
        1,
        '2025-09-18 18:16:20',
        "OffDuty"
    ),
    (
        2,
        '2025-09-19 8:21:56',
        "OnDuty"
    ),
    (
        2,
        '2025-09-19 19:42:16',
        "OffDuty"
    ),
    (
        3,
        '2025-09-20 8:46:39',
        "OnDuty"
    ),
    (
        3,
        '2025-09-20 18:55:05',
        "OffDuty"
    ),
    (
        4,
        '2025-09-21 8:39:57',
        "OnDuty"
    ),
    (
        4,
        '2025-09-21 19:03:57',
        "OffDuty"
    ),