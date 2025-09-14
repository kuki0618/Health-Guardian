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
        '赵忆萱',
        '算法工程师',
        '散步',
        26
    );

INSERT INTO
    employees
VALUES (
        "604157341328085868",
        '潘可欣',
        '产品经理',
        '游泳',
        23
    );

INSERT INTO
    employees
VALUES (
        "03366627182021511253",
        '司梓岐',
        '会计',
        '篮球',
        26
    );

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