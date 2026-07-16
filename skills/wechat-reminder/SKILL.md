---
name: wechat-reminder
description: "Create, list, and cancel persistent server-side reminders that proactively send a WeChat message at the requested time. Use when the user says 提醒我, 定个闹钟, 几分钟后叫我, 到点告诉我, 今晚/明天几点提醒, 查看提醒, or 取消提醒. This is a real proactive WeChat reminder, not a blocking sleep command."
---

# WeChat Reminder

Create real persistent reminders with:

```sh
python3 /home/ubuntu/learning-loop/scripts/reminder.py <command>
```

## Rules

- Never use `sleep`, `at`, a foreground shell wait, or a conversational promise as a substitute for a reminder.
- A reminder is created only when `reminder.py` returns an ID and `PENDING` status.
- The `learning-loop-reminder` system service checks SQLite every 15 seconds and proactively sends due messages through WeChat. It works after the conversation ends and survives Pi restarts.
- Confirm the exact due time and reminder ID to the user.
- Interpret relative times in Asia/Shanghai server local time.
- For an `HH:MM` time already passed today, the CLI schedules tomorrow.
- Use short, self-contained messages that make sense when received later.
- This supports reminders, not guaranteed alarm-clock sound. Delivery depends on WeChat/network availability and may be delayed by roughly 15–60 seconds.

## Commands

```sh
# Relative minutes (decimals allowed for testing; normally use whole minutes)
python3 /home/ubuntu/learning-loop/scripts/reminder.py in 1 "⏰ 一分钟到了，该睡觉了"
python3 /home/ubuntu/learning-loop/scripts/reminder.py in 25 "⏰ 休息结束，回来学习"

# Exact local time; accepts HH:MM or ISO datetime
python3 /home/ubuntu/learning-loop/scripts/reminder.py at 23:30 "⏰ 到点睡觉"
python3 /home/ubuntu/learning-loop/scripts/reminder.py at "2026-07-17 07:30" "⏰ 起床"

# Manage reminders
python3 /home/ubuntu/learning-loop/scripts/reminder.py list
python3 /home/ubuntu/learning-loop/scripts/reminder.py list --all
python3 /home/ubuntu/learning-loop/scripts/reminder.py cancel 12
```

If creation fails, report the exact error. Do not claim that a timer was set.
