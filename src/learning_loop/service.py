import json
from datetime import datetime,timedelta
from .db import connect,init_db
from .domain import *

def now(): return datetime.now().replace(microsecond=0)
def iso(v): return v.isoformat(sep=" ") if v else None
def row(r): return dict(r) if r else None
class RuleError(ValueError): pass

def event(c,t,i,a,p=None): c.execute("INSERT INTO events(entity_type,entity_id,action,payload) VALUES(?,?,?,?)",(t,i,a,json.dumps(p,ensure_ascii=False) if p else None))
def schedule_guard(c,uid,subject,title,due):
    c.execute("UPDATE reminders SET status='CANCELLED',updated_at=CURRENT_TIMESTAMP WHERE unit_id=? AND kind='GUARD' AND status='PENDING'",(uid,))
    msg=f"⏰ 学习护栏到了：{subject}｜{title}\n请选择：回来闭环、延长10–30分钟、暂停并记录下一步，或休息后继续。"
    c.execute("INSERT INTO reminders(unit_id,kind,due_at,message) VALUES(?,?,?,?)",(uid,'GUARD',iso(due),msg))
def cancel_guard(c,uid): c.execute("UPDATE reminders SET status='CANCELLED',updated_at=CURRENT_TIMESTAMP WHERE unit_id=? AND kind='GUARD' AND status='PENDING'",(uid,))
def get_unit(c,uid):
    x=c.execute("SELECT * FROM units WHERE id=?",(uid,)).fetchone()
    if not x: raise RuleError("学习单元不存在")
    return x

def start_unit(subject,title,objective,practice_plan,guard_minutes=60,path=None):
    if subject not in SUBJECTS: raise RuleError("学科必须是数学、408、英语或政治")
    if not 10<=guard_minutes<=180: raise RuleError("时间护栏必须为10到180分钟")
    init_db(path); c=connect(path)
    try:
        existing=c.execute("SELECT id,title,flow_status FROM units WHERE subject=? AND flow_status IN ('ACTIVE','PENDING')",(subject,)).fetchone()
        if existing: raise RuleError(f"{subject}已有未结束单元 #{existing['id']} {existing['title']}")
        pending=c.execute("SELECT count(*) n FROM units WHERE flow_status='PENDING'").fetchone()['n']
        if pending>=3: raise RuleError("全局待闭环单元已达3个，请先处理旧单元")
        due=now()+timedelta(minutes=guard_minutes)
        cur=c.execute("INSERT INTO units(subject,title,objective,practice_plan,guard_minutes,guard_due_at) VALUES(?,?,?,?,?,?)",(subject,title.strip(),objective.strip(),practice_plan.strip(),guard_minutes,iso(due)))
        uid=cur.lastrowid; schedule_guard(c,uid,subject,title.strip(),due); event(c,"unit",uid,"START",{"guard_due_at":iso(due)}); c.commit(); return row(get_unit(c,uid))
    finally:c.close()
def list_units(path=None,subject=None,flow=None,mastery=None):
    init_db(path); c=connect(path); q="SELECT * FROM units WHERE 1=1"; p=[]
    for col,val in (("subject",subject),("flow_status",flow),("mastery_status",mastery)):
        if val:q+=f" AND {col}=?";p.append(val)
    q+=" ORDER BY updated_at DESC,id DESC"; out=[row(x) for x in c.execute(q,p)];c.close();return out
def unit_detail(uid,path=None):
    init_db(path);c=connect(path)
    try:
        u=row(get_unit(c,uid));u['prompts']=[row(x) for x in c.execute("SELECT * FROM review_prompts WHERE unit_id=? AND active=1",(uid,))];u['reviews']=[row(x) for x in c.execute("SELECT * FROM reviews WHERE unit_id=? ORDER BY id DESC",(uid,))];u['audits']=[row(x) for x in c.execute("SELECT * FROM audits WHERE unit_id=? ORDER BY id DESC",(uid,))];return u
    finally:c.close()
def set_stage(uid,stage,path=None):
    stage=Stage(stage);init_db(path);c=connect(path)
    try:
        u=get_unit(c,uid)
        if u['flow_status']!='ACTIVE':raise RuleError("只有活动单元可以推进关卡")
        order=list(Stage)
        if order.index(stage)>order.index(Stage(u['stage']))+1:raise RuleError("不能跨越学习关卡")
        c.execute("UPDATE units SET stage=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(stage,uid));event(c,"unit",uid,"STAGE",{"stage":stage});c.commit();return unit_detail(uid,path)
    finally:c.close()
def checkpoint(uid,action,minutes=None,position=None,blocker=None,next_action=None,path=None):
    init_db(path);c=connect(path)
    try:
        u=get_unit(c,uid)
        if u['flow_status'] not in ('ACTIVE','PENDING'):raise RuleError("该单元已经结束")
        if action=='extend':
            if u['guard_extensions']>=2:raise RuleError("已经延长两次，请拆分或暂停")
            m=int(minutes or 20)
            if not 10<=m<=30:raise RuleError("每次只能延长10到30分钟")
            due=now()+timedelta(minutes=m); c.execute("UPDATE units SET flow_status='ACTIVE',guard_due_at=?,guard_extensions=guard_extensions+1,updated_at=CURRENT_TIMESTAMP WHERE id=?",(iso(due),uid)); schedule_guard(c,uid,u['subject'],u['title'],due)
        elif action in ('pause','rest'):
            if not next_action:raise RuleError("暂停时必须记录下一步")
            c.execute("UPDATE units SET flow_status='PENDING',current_position=?,blocker=?,next_action=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(position,blocker,next_action,uid)); cancel_guard(c,uid)
        elif action=='resume':
            due=now()+timedelta(minutes=u['guard_minutes']); c.execute("UPDATE units SET flow_status='ACTIVE',guard_due_at=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(iso(due),uid)); schedule_guard(c,uid,u['subject'],u['title'],due)
        elif action=='close': c.execute("UPDATE units SET stage='PRACTICING',updated_at=CURRENT_TIMESTAMP WHERE id=?",(uid,)); cancel_guard(c,uid)
        else:raise RuleError("未知检查点动作")
        event(c,"unit",uid,"CHECKPOINT",{"action":action});c.commit();return unit_detail(uid,path)
    finally:c.close()
def submit_practice(uid,practice_type,independence,result,note="",metrics=None,path=None):
    init_db(path);c=connect(path)
    try:
        u=get_unit(c,uid)
        if u['flow_status']!='ACTIVE':raise RuleError("请先恢复单元")
        c.execute("UPDATE units SET practice_type=?,independence=?,practice_result=?,practice_note=?,practice_metrics=?,stage='EXTRACTING',updated_at=CURRENT_TIMESTAMP WHERE id=?",(practice_type,independence,result,note,json.dumps(metrics or {},ensure_ascii=False),uid));event(c,"unit",uid,"PRACTICE");c.commit();return unit_detail(uid,path)
    finally:c.close()
def submit_extraction(uid,content,question,path=None):
    if len(content.strip())<12:raise RuleError("自己的话提炼过短，请包含识别信号和核心动作")
    if len(question.strip())<5:raise RuleError("至少提供一个可主动提取的复盘问题")
    init_db(path);c=connect(path)
    try:
        u=get_unit(c,uid)
        if not u['practice_result']:raise RuleError("必须先提交独立实践证据")
        c.execute("UPDATE units SET extraction=?,stage='ASSESSING',updated_at=CURRENT_TIMESTAMP WHERE id=?",(content.strip(),uid));c.execute("INSERT INTO extraction_versions(unit_id,content) VALUES(?,?)",(uid,content.strip()));c.execute("INSERT INTO review_prompts(unit_id,question,answer) VALUES(?,?,?)",(uid,question.strip(),content.strip()));event(c,"unit",uid,"EXTRACT");c.commit();return unit_detail(uid,path)
    finally:c.close()
def save_audit(uid,data,path=None):
    init_db(path);c=connect(path)
    try:
        get_unit(c,uid); fields=('provider','model','verdict','possible_error','key_gap','follow_up_question','importance_suggestion','mastery_suggestion','evidence_level')
        vals=[data.get(k) for k in fields];c.execute(f"INSERT INTO audits(unit_id,{','.join(fields)},raw_json) VALUES(?,{','.join('?' for _ in fields)},?)",[uid,*vals,json.dumps(data,ensure_ascii=False)])
        if data.get('follow_up_question'):c.execute("UPDATE units SET follow_up_question=?,follow_up_status='OPEN' WHERE id=?",(data['follow_up_question'],uid))
        event(c,"unit",uid,"AUDIT");c.commit();return unit_detail(uid,path)
    finally:c.close()
def close_unit(uid,importance,follow_up_action='none',follow_up_answer=None,path=None):
    importance=Importance(importance);init_db(path);c=connect(path)
    try:
        u=get_unit(c,uid)
        if not u['practice_result'] or not u['extraction']:raise RuleError("关闭前必须有实践证据和自己的话提炼")
        if u['follow_up_status']=='OPEN' and follow_up_action not in ('answer','correct_ai','defer'):raise RuleError("AI关键追问必须回答、纠正或明确延后")
        mastery=Mastery.FRAGILE if follow_up_action=='defer' or u['practice_result']=='FAILED' else Mastery.UNTESTED
        c.execute("UPDATE units SET flow_status='CLOSED',stage='DONE',mastery_status=?,importance=?,follow_up_status=?,closed_at=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(mastery,importance,follow_up_action.upper(),iso(now()),uid)); cancel_guard(c,uid)
        days=1 if mastery==Mastery.FRAGILE else (3 if importance==Importance.CORE else 5)
        c.execute("INSERT INTO reviews(unit_id,pool,due_at,priority) VALUES(?,?,?,?)",(uid,ReviewPool.SHORT,iso(now()+timedelta(days=days)),100 if importance==Importance.CORE else 50))
        event(c,"unit",uid,"CLOSE",{"mastery":mastery});c.commit();return unit_detail(uid,path)
    finally:c.close()
