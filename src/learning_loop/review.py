from datetime import datetime,timedelta
from .db import connect,init_db
from .domain import *
from .service import row,get_unit,event,RuleError,iso,now

def due_reviews(subject,limit=5,path=None):
    init_db(path);c=connect(path)
    q='''SELECT r.*,u.title,u.subject,u.importance,u.mastery_status FROM reviews r JOIN units u ON u.id=r.unit_id
         WHERE r.status='QUEUED' AND u.subject=? AND (r.due_at IS NULL OR r.due_at<=?)
         ORDER BY r.priority DESC,COALESCE(r.due_at,'') ASC LIMIT ?'''
    out=[]
    for x in c.execute(q,(subject,iso(now()),limit)):
        d=row(x);d['prompts']=[row(p) for p in c.execute("SELECT id,question,kind FROM review_prompts WHERE unit_id=? AND active=1",(x['unit_id'],))];out.append(d)
    c.close();return out

def submit_review(review_id,recall_result,application_result,note='',path=None):
    recall=TestResult(recall_result);app=TestResult(application_result);init_db(path);c=connect(path)
    try:
        r=c.execute("SELECT * FROM reviews WHERE id=? AND status='QUEUED'",(review_id,)).fetchone()
        if not r:raise RuleError("复盘任务不存在或已完成")
        u=get_unit(c,r['unit_id'])
        passes=c.execute("SELECT count(*) n FROM reviews WHERE unit_id=? AND recall_result='INDEPENDENT' AND application_result='INDEPENDENT'",(u['id'],)).fetchone()['n']
        mastery=mastery_from_results(recall,app,Mastery(u['mastery_status']),passes+1)
        c.execute("UPDATE reviews SET status='DONE',recall_result=?,application_result=?,note=?,reviewed_at=? WHERE id=?",(recall,app,note,iso(now()),review_id))
        c.execute("UPDATE units SET mastery_status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(mastery,u['id']))
        if mastery==Mastery.FRAGILE: pool,days,priority=ReviewPool.SHORT,1,110
        elif mastery==Mastery.DEVELOPING: pool,days,priority=ReviewPool.SHORT,2,90
        elif mastery==Mastery.RELIABLE: pool,days,priority=ReviewPool.LONG,7,40
        elif mastery==Mastery.MAINTAINED: pool,days,priority=ReviewPool.LONG,21,20
        else: pool,days,priority=ReviewPool.SHORT,3,60
        c.execute("INSERT INTO reviews(unit_id,pool,due_at,priority) VALUES(?,?,?,?)",(u['id'],pool,iso(now()+timedelta(days=days)),priority))
        event(c,"review",review_id,"COMPLETE",{"mastery":mastery,"next_pool":pool});c.commit()
        return {"review_id":review_id,"unit_id":u['id'],"mastery_status":mastery,"next_pool":pool,"next_due_at":iso(now()+timedelta(days=days))}
    finally:c.close()
def record_entry(subject,action,reason=None,batch_size=None,path=None):
    init_db(path);c=connect(path);cur=c.execute("INSERT INTO subject_entries(subject,action,reason,batch_size) VALUES(?,?,?,?)",(subject,action,reason,batch_size));c.commit();c.close();return {"id":cur.lastrowid}
def friction(content,path=None):
    init_db(path);c=connect(path);cur=c.execute("INSERT INTO friction_logs(content) VALUES(?)",(content.strip(),));c.commit();c.close();return {"id":cur.lastrowid}
def dashboard(path=None):
    init_db(path);c=connect(path)
    today=datetime.now().date().isoformat()
    stats={}
    stats['active']=[row(x) for x in c.execute("SELECT * FROM units WHERE flow_status IN ('ACTIVE','PENDING') ORDER BY subject")]
    stats['closed_today']=c.execute("SELECT count(*) n FROM units WHERE date(closed_at)=?",(today,)).fetchone()['n']
    stats['due_by_subject']={s:c.execute("SELECT count(*) n FROM reviews r JOIN units u ON u.id=r.unit_id WHERE r.status='QUEUED' AND u.subject=? AND (r.due_at IS NULL OR r.due_at<=?)",(s,iso(now()))).fetchone()['n'] for s in SUBJECTS}
    stats['mastery']={x['mastery_status']:x['n'] for x in c.execute("SELECT mastery_status,count(*) n FROM units GROUP BY mastery_status")}
    c.close();return stats
def experiment(path=None):
    init_db(path);c=connect(path)
    ended=c.execute("SELECT count(*) n FROM units WHERE flow_status IN ('CLOSED','SKIPPED','ARCHIVED')").fetchone()['n'];closed=c.execute("SELECT count(*) n FROM units WHERE flow_status='CLOSED' AND practice_result IS NOT NULL AND extraction IS NOT NULL").fetchone()['n']
    offered=c.execute("SELECT COALESCE(sum(batch_size),0) n FROM subject_entries WHERE action IN ('START','REDUCE')").fetchone()['n'];done=c.execute("SELECT count(*) n FROM reviews WHERE status='DONE'").fetchone()['n']
    out={"closed_loop_rate":closed/ended if ended else None,"review_execution_rate":done/offered if offered else None,"units_ended":ended,"units_closed":closed,"reviews_offered":offered,"reviews_done":done,"frictions":[row(x) for x in c.execute("SELECT * FROM friction_logs ORDER BY created_at DESC")],"mastery_transitions":[row(x) for x in c.execute("SELECT * FROM events WHERE action='COMPLETE' ORDER BY created_at DESC")]};c.close();return out
