---
name: learning-loop
description: Run the user's postgraduate-exam learning workflow: enter a subject, start/resume a small learning unit, enforce independent practice and own-words extraction, audit an extraction, close or pause a unit, handle guard checkpoints, perform active reviews, and report the seven-day experiment. Use for “开始学数学/408/英语/政治”, “开始一个学习单元”, “回来闭环”, “我做完题了”, “用自己的话说”, “复盘”, “暂停/继续”, or “看看学习闭环数据”.
---

# Learning Loop

Use the deterministic CLI. Never edit SQLite directly and never bypass a rejected transition.

```sh
python3 /home/ubuntu/learning-loop/skills/learning-loop/scripts/learning_loop.py <command...>
```

## Workflow

1. On entering a subject, run `due <subject>` before starting new material. Offer at most 5 items. The user may reduce, replace, or explicitly skip with a reason.
2. Start a unit with a concrete objective, practice plan, and 10–180 minute guard.
3. Stay quiet while the user studies. At the guard time, ask: close, extend 10–30 minutes, split, pause with next action, or rest then continue. Never infer completion from elapsed time.
4. On “回来闭环”, collect practice evidence first:
   - practice type
   - independence: INDEPENDENT/HINTED/REVEALED
   - result: SUCCESS/PARTIAL/FAILED
   - one key discovery or blocker
5. Then request own-words extraction with one core prompt: “这个内容能解决什么问题？看到什么信号时，我具体应该怎么做？” Require a review question.
6. Audit the extraction yourself. Return and save structured JSON with at most one material follow-up:
```json
{"provider":"pi-agent","model":"current","verdict":"ok|needs_revision","possible_error":null,"key_gap":null,"follow_up_question":null,"importance_suggestion":"CORE|NORMAL|LOW","mastery_suggestion":"UNTESTED|FRAGILE|DEVELOPING","evidence_level":"GENERAL|REFERENCE|OBJECTIVE"}
```
7. A material follow-up must be answered, corrected with stronger evidence, or explicitly deferred. Deferral closes flow at no better than FRAGILE and schedules early review.
8. AI advice never grants CLOSED, RELIABLE, or MAINTAINED. The CLI owns all state.
9. During review, show only saved questions first. Record recall and application separately as INDEPENDENT/HINTED/REVEALED/FAILED/NOT_TESTED.

## Commands

```sh
... dashboard
... start 数学 "抽象逆矩阵" --objective "识别并使用互逆关系" --practice "独立做同类题" --guard 60
... units --subject 数学
... show 1
... checkpoint 1 close
... checkpoint 1 extend --minutes 20
... checkpoint 1 pause --next-action "下次完成第3题"
... checkpoint 1 resume
... practice 1 --type 做题 --independence INDEPENDENT --result SUCCESS --note "独立完成3题"
... extract 1 "看到AB=E时……" --question "出现AB=E时优先想到什么？"
... audit 1 '{...}'
... close 1 --importance CORE --follow-up-action none
... due 数学 --limit 5
... review 1 --recall INDEPENDENT --application HINTED --note "变式题需要提示"
... entry 数学 START --batch-size 5
... entry 数学 SKIP --reason "高精力先攻难题"
... friction "提炼输入太重"
... experiment
```

If a command fails, report its exact error and guide the user to a legal next action. Do not silently retry with a weaker transition.
