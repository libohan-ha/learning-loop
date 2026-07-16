#!/usr/bin/env python3
import argparse,json,os,sqlite3
from datetime import datetime,timedelta
from pathlib import Path
DB=Path(os.getenv('LEARNING_LOOP_DB','/home/ubuntu/learning-loop-data/learning_loop.db'))
def conn():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def output(x):print(json.dumps(x,ensure_ascii=False,indent=2))
def main():
 p=argparse.ArgumentParser(prog='wechat-reminder');s=p.add_subparsers(dest='cmd',required=True)
 x=s.add_parser('in');x.add_argument('minutes',type=float);x.add_argument('message')
 x=s.add_parser('at');x.add_argument('time');x.add_argument('message')
 x=s.add_parser('list');x.add_argument('--all',action='store_true')
 x=s.add_parser('cancel');x.add_argument('id',type=int)
 a=p.parse_args();c=conn()
 if a.cmd=='in':
  if not 0<a.minutes<=10080:raise SystemExit('minutes must be >0 and <=10080')
  due=datetime.now()+timedelta(minutes=a.minutes)
  cur=c.execute("INSERT INTO general_reminders(due_at,message) VALUES(?,?)",(due.isoformat(sep=' ',timespec='seconds'),a.message.strip()));c.commit();output({'id':cur.lastrowid,'due_at':due.isoformat(sep=' ',timespec='seconds'),'message':a.message,'status':'PENDING'})
 elif a.cmd=='at':
  raw=a.time.strip();due=datetime.fromisoformat(raw if ' ' in raw or 'T' in raw else datetime.now().date().isoformat()+' '+raw)
  if due<=datetime.now():due+=timedelta(days=1)
  cur=c.execute("INSERT INTO general_reminders(due_at,message) VALUES(?,?)",(due.isoformat(sep=' ',timespec='seconds'),a.message.strip()));c.commit();output({'id':cur.lastrowid,'due_at':due.isoformat(sep=' ',timespec='seconds'),'message':a.message,'status':'PENDING'})
 elif a.cmd=='list':
  q="SELECT * FROM general_reminders"+("" if a.all else " WHERE status='PENDING'")+" ORDER BY due_at";output([dict(x) for x in c.execute(q)])
 else:
  cur=c.execute("UPDATE general_reminders SET status='CANCELLED',updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='PENDING'",(a.id,));c.commit();output({'id':a.id,'cancelled':cur.rowcount>0})
 c.close()
if __name__=='__main__':main()
