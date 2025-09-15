CREATE TABLE employees (
    userid VARCHAR(50) PRIMARY KEY, -- 员工ID（主键）
    name VARCHAR(50) NOT NULL, -- 姓名
    title VARCHAR(50), -- 职位
    hobby VARCHAR(100), -- 爱好
    age INT -- 年龄
);

INSERT INTO
    employees
VALUES (
        "manager4585",
        '小忆',
        '算法工程师',
        '散步',
        26
    );

INSERT INTO
    employees
VALUES (
        "604157341328085868",
        '小潘',
        '产品经理',
        '游泳',
        23
    );

INSERT INTO
    employees
VALUES (
        "03366627182021511253",
        '小岐',
        '会计',
        '篮球',
        26
    );

'''
CREATE TABLE clock_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY, -- 序号（自增主键）
    date DATE NOT NULL, -- 日期
    employee_id INT NOT NULL, -- 员工ID（外键）
    clock_in_time DATETIME, -- 签到时间
    clock_out_time DATETIME, -- 签退时间
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
    task_id INT NOT NULL, -- 外键，关联到主表的任务ID
    start_datetime DATETIME,
    end_datetime DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

CREATE TABLE health_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- 外键，关联到主表的任务ID
    data_time DATETIME,
    msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES online_status (id) ON DELETE CASCADE
);

CREATE TABLE attendance_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL, -- 外键，关联到主表的任务ID
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

-- 获取刚插入的任务ID（假设为 1），然后向时间段子表插入多个时间段
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
        "您从9点到11点连续在线工作,建议起身活动一下,深呼吸或远眺放松眼睛。今日气温较高(32℃),请多喝水防暑降温哦！"
    ),
    (
        2,
        '2025-09-06 15:00:00',
        "您下午3点至5点持续在岗,记得适当起身走动,避免久坐。今天温度29℃,午后炎热,请及时补水,保持水分充足～"
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