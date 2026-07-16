import argparse,json,sys
from . import service as s
from . import review as r
from .db import init_db

def out(x):print(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def main():
 p=argparse.ArgumentParser(prog='learning-loop');p.add_argument('--db');q=p.add_subparsers(dest='cmd',required=True)
 q.add_parser('init')
 x=q.add_parser('dashboard')
 x=q.add_parser('start');x.add_argument('subject');x.add_argument('title');x.add_argument('--objective',required=True);x.add_argument('--practice',required=True);x.add_argument('--guard',type=int,default=60)
 x=q.add_parser('units');x.add_argument('--subject');x.add_argument('--flow');x.add_argument('--mastery')
 x=q.add_parser('show');x.add_argument('id',type=int)
 x=q.add_parser('practice');x.add_argument('id',type=int);x.add_argument('--type',required=True);x.add_argument('--independence',required=True);x.add_argument('--result',required=True);x.add_argument('--note',default='')
 x=q.add_parser('extract');x.add_argument('id',type=int);x.add_argument('content');x.add_argument('--question',required=True)
 x=q.add_parser('checkpoint');x.add_argument('id',type=int);x.add_argument('action');x.add_argument('--minutes',type=int);x.add_argument('--position');x.add_argument('--blocker');x.add_argument('--next-action')
 x=q.add_parser('audit');x.add_argument('id',type=int);x.add_argument('json')
 x=q.add_parser('close');x.add_argument('id',type=int);x.add_argument('--importance',required=True);x.add_argument('--follow-up-action',default='none')
 x=q.add_parser('due');x.add_argument('subject');x.add_argument('--limit',type=int,default=5)
 x=q.add_parser('review');x.add_argument('id',type=int);x.add_argument('--recall',required=True);x.add_argument('--application',required=True);x.add_argument('--note',default='')
 x=q.add_parser('entry');x.add_argument('subject');x.add_argument('action');x.add_argument('--reason');x.add_argument('--batch-size',type=int)
 x=q.add_parser('friction');x.add_argument('content')
 q.add_parser('experiment')
 a=p.parse_args();path=a.db
 try:
  if a.cmd=='init':init_db(path);z={'ok':True}
  elif a.cmd=='dashboard':z=r.dashboard(path)
  elif a.cmd=='start':z=s.start_unit(a.subject,a.title,a.objective,a.practice,a.guard,path)
  elif a.cmd=='units':z=s.list_units(path,a.subject,a.flow,a.mastery)
  elif a.cmd=='show':z=s.unit_detail(a.id,path)
  elif a.cmd=='practice':z=s.submit_practice(a.id,a.type,a.independence,a.result,a.note,path=path)
  elif a.cmd=='extract':z=s.submit_extraction(a.id,a.content,a.question,path)
  elif a.cmd=='checkpoint':z=s.checkpoint(a.id,a.action,a.minutes,a.position,a.blocker,a.next_action,path)
  elif a.cmd=='audit':z=s.save_audit(a.id,json.loads(a.json),path)
  elif a.cmd=='close':z=s.close_unit(a.id,a.importance,a.follow_up_action,path=path)
  elif a.cmd=='due':z=r.due_reviews(a.subject,a.limit,path)
  elif a.cmd=='review':z=r.submit_review(a.id,a.recall,a.application,a.note,path)
  elif a.cmd=='entry':z=r.record_entry(a.subject,a.action,a.reason,a.batch_size,path)
  elif a.cmd=='friction':z=r.friction(a.content,path)
  else:z=r.experiment(path)
  out(z);return 0
 except Exception as e:out({'error':str(e),'type':type(e).__name__});return 1
if __name__=='__main__':raise SystemExit(main())
