from typing import Any,Literal,Optional
from fastapi import FastAPI,HTTPException,Header,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
import os,secrets
from . import service as s
from . import review as rv
from .db import init_db

app=FastAPI(title="Learning Loop",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("LEARNING_LOOP_ORIGINS","http://localhost:5173").split(','),allow_methods=['*'],allow_headers=['*'])
def auth(authorization:Optional[str]=Header(None)):
    token=os.getenv('LEARNING_LOOP_TOKEN')
    if token and (not authorization or not authorization.startswith('Bearer ') or not secrets.compare_digest(authorization[7:],token)):raise HTTPException(401,'invalid token')
def run(fn,*a,**kw):
    try:return fn(*a,**kw)
    except (s.RuleError,ValueError) as e:raise HTTPException(409,str(e))
class Start(BaseModel):subject:str;title:str;objective:str;practice_plan:str;guard_minutes:int=Field(60,ge=10,le=180)
class Practice(BaseModel):practice_type:str;independence:Literal['INDEPENDENT','HINTED','REVEALED'];result:Literal['SUCCESS','PARTIAL','FAILED'];note:str='';metrics:dict[str,Any]={}
class Extraction(BaseModel):content:str;question:str
class Checkpoint(BaseModel):action:Literal['extend','pause','rest','resume','close'];minutes:Optional[int]=None;position:Optional[str]=None;blocker:Optional[str]=None;next_action:Optional[str]=None
class Close(BaseModel):importance:Literal['CORE','NORMAL','LOW'];follow_up_action:Literal['none','answer','correct_ai','defer']='none';follow_up_answer:Optional[str]=None
class ReviewResult(BaseModel):recall_result:str;application_result:str;note:str=''
class Entry(BaseModel):action:str;reason:Optional[str]=None;batch_size:Optional[int]=None
class Friction(BaseModel):content:str
class Audit(BaseModel):provider:Optional[str]=None;model:Optional[str]=None;verdict:Optional[str]=None;possible_error:Optional[str]=None;key_gap:Optional[str]=None;follow_up_question:Optional[str]=None;importance_suggestion:Optional[str]=None;mastery_suggestion:Optional[str]=None;evidence_level:str='NONE';raw:dict[str,Any]={}
@app.on_event('startup')
def startup():init_db()
@app.get('/health')
def health():return {'status':'ok','service':'learning-loop'}
@app.get('/api/dashboard',dependencies=[Depends(auth)])
def dashboard():return rv.dashboard()
@app.get('/api/units',dependencies=[Depends(auth)])
def units(subject:str|None=None,flow:str|None=None,mastery:str|None=None):return {'units':s.list_units(subject=subject,flow=flow,mastery=mastery)}
@app.post('/api/units',dependencies=[Depends(auth)])
def start(x:Start):return run(s.start_unit,**x.model_dump())
@app.get('/api/units/{uid}',dependencies=[Depends(auth)])
def detail(uid:int):return run(s.unit_detail,uid)
@app.post('/api/units/{uid}/practice',dependencies=[Depends(auth)])
def practice(uid:int,x:Practice):return run(s.submit_practice,uid,**x.model_dump())
@app.post('/api/units/{uid}/extraction',dependencies=[Depends(auth)])
def extraction(uid:int,x:Extraction):return run(s.submit_extraction,uid,x.content,x.question)
@app.post('/api/units/{uid}/checkpoint',dependencies=[Depends(auth)])
def checkpoint(uid:int,x:Checkpoint):return run(s.checkpoint,uid,**x.model_dump())
@app.post('/api/units/{uid}/audit',dependencies=[Depends(auth)])
def audit(uid:int,x:Audit):
    d=x.model_dump();d['raw_json']=d.pop('raw');return run(s.save_audit,uid,d)
@app.post('/api/units/{uid}/close',dependencies=[Depends(auth)])
def close(uid:int,x:Close):return run(s.close_unit,uid,**x.model_dump())
@app.get('/api/reviews/due',dependencies=[Depends(auth)])
def due(subject:str,limit:int=5):return {'reviews':rv.due_reviews(subject,min(max(limit,1),10))}
@app.post('/api/reviews/{rid}/result',dependencies=[Depends(auth)])
def result(rid:int,x:ReviewResult):return run(rv.submit_review,rid,**x.model_dump())
@app.post('/api/subjects/{subject}/entry',dependencies=[Depends(auth)])
def entry(subject:str,x:Entry):return rv.record_entry(subject,**x.model_dump())
@app.post('/api/friction',dependencies=[Depends(auth)])
def friction(x:Friction):return rv.friction(x.content)
@app.get('/api/experiment',dependencies=[Depends(auth)])
def experiment():return rv.experiment()
