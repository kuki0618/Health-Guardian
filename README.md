# HealthGuardian 

一个基于"事件驱动 + 规则引擎 + LLM 润色"的办公健康辅助服务，通过分析用户签到、在线状态、日程、步数和天气等信息，提供个性化的健康提醒。

> 基于 FastAPI + DeepSeek + LangChain + MySQL 的技术栈实现

---

## ? 核心价值

- **智能时机判断**：结合用户日程表，只在合适时间发送提醒
- **个性化内容**：基于步数、天气、时间早晚和用户喜好生成提醒
- **多源数据融合**：整合签到、在线状态、日程、运动、天气数据
- **LLM润色优化**：使用DeepSeek模型让提醒更自然友好

## ? 数据源说明

| 数据源 | 获取频率 | 用途 |
|--------|----------|------|
| 签到信息 | 实时 | 判断用户在岗状态 |
| 在线状态 | 每2小时 | 检测久坐行为 |
| 日程表 | 每日同步 | 判断是否适合发送提醒 |
| 运动步数 | 每日同步 | 个性化活动建议 |
| 天气信息 | 每3小时 | 环境适应性提醒 |

## ? 处理流程

1. **数据采集** → 定时从钉钉API获取多源数据
2. **久坐检测** → 每2小时分析用户活动状态
3. **情境判断** → 结合日程表决定是否发送
4. **个性化生成** → 基于用户上下文生成建议
5. **LLM润色** → 使用DeepSeek优化提醒文案
6. **消息推送** → 通过钉钉工作通知发送
7. **反馈处理** → 收集用户互动反馈

## ?? 核心数据表

```sql
-- 用户状态表（存储在线状态检测结果）
CREATE TABLE user_status (
    user_id VARCHAR(64),
    status_time TIMESTAMP,
    is_active BOOLEAN,
    device_type VARCHAR(32)
);

-- 日程表（会议和任务安排）
CREATE TABLE schedules (
    user_id VARCHAR(64),
    schedule_time TIMESTAMP,
    title VARCHAR(255),
    is_busy BOOLEAN  -- 是否重要日程
);

-- 提醒记录表
CREATE TABLE health_reminders (
    user_id VARCHAR(64),
    reminder_time TIMESTAMP,
    reminder_type VARCHAR(64),
    content TEXT,
    status VARCHAR(32)
);
```

## ?? 系统配置

### 环境变量
```bash
# 钉钉配置
DINGTALK_APP_KEY=your_app_key
DINGTALK_APP_SECRET=your_app_secret

# DeepSeek配置
DEEPSEEK_API_KEY=your_api_key

# 数据库配置
DATABASE_URL=mysql://user:pass@localhost/db
```

### 主要参数
```python
# 久坐检测阈值（分钟）
SEDENTARY_THRESHOLD = 120

# 提醒冷却时间（分钟）
REMINDER_COOLDOWN = 30

# LLM调用超时（秒）
LLM_TIMEOUT = 10
```

## ? 部署运行

1. **安装依赖**
```bash
pip install fastapi uvicorn mysql-connector-python langchain
```

2. **启动服务**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **配置定时任务**
```bash
# 每2小时执行久坐检测
0 */2 * * * curl -X POST http://localhost:8000/check-sedentary
```

## ? 监控指标

| 指标名称 | 监控方式 | 预期目标 |
|----------|----------|----------|
| 久坐检测准确率 | 日志分析 | >90% |
| 提醒接受率 | 反馈统计 | >70% |
| API响应时间 | 性能监控 | <200ms |
| LLM调用成功率 | 错误日志 | >95% |

## ? 核心功能模块

### 1. 久坐检测服务
- 每2小时检查用户在线状态
- 结合日程表判断发送时机
- 避免会议期间打扰用户

### 2. 个性化提醒生成
- 基于步数推荐活动强度
- 根据天气调整建议内容
- 考虑时间早晚因素

### 3. LLM润色服务
- 使用DeepSeek优化文案
- 保持专业且友好的语气
- 控制生成长度适中

### 4. 反馈处理机制
- 收集用户正面/负面反馈
- 优化后续提醒策略
- 统计接受率指标

## ? 特色功能

1. **智能免打扰**：自动识别会议时段，避免重要时段发送提醒
2. **天气适应性**：根据天气状况调整活动建议（室内/室外）
3. **进度感知**：基于当日步数提供个性化运动建议
4. **时段优化**：早晚不同风格的提醒文案

## ? 实施计划

1. **第一阶段**：实现基础数据采集和久坐检测
2. **第二阶段**：集成DeepSeek进行文案优化
3. **第三阶段**：添加用户反馈和个性化学习
4. **第四阶段**：完善监控和报表功能

