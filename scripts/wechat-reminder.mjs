import {WeChatBot} from '/home/ubuntu/.pi/agent/npm/node_modules/@wechatbot/wechatbot/dist/index.js';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
const db=process.env.LEARNING_LOOP_DB||'/home/ubuntu/learning-loop-data/learning_loop.db';
const py=process.env.LEARNING_LOOP_PYTHON||'/home/ubuntu/learning-loop/.venv/bin/python';
const code=`import sqlite3,json,sys\np=sys.argv[1];c=sqlite3.connect(p);c.row_factory=sqlite3.Row\nif sys.argv[2]=='claim':\n r=c.execute("SELECT id,message,'unit' source FROM reminders WHERE status='PENDING' AND due_at<=datetime('now','localtime') UNION ALL SELECT id,message,'general' source FROM general_reminders WHERE status='PENDING' AND due_at<=datetime('now','localtime') ORDER BY id LIMIT 1").fetchone()\n if r:\n  t='reminders' if r['source']=='unit' else 'general_reminders';c.execute(f"UPDATE {t} SET status='SENDING',attempts=attempts+1,updated_at=CURRENT_TIMESTAMP WHERE id=?",(r['id'],));c.commit();print(json.dumps(dict(r),ensure_ascii=False))\nelif sys.argv[2] in ('done','fail'):\n t='reminders' if sys.argv[4]=='unit' else 'general_reminders'\n if sys.argv[2]=='done':c.execute(f"UPDATE {t} SET status='SENT',sent_at=CURRENT_TIMESTAMP,updated_at=CURRENT_TIMESTAMP,last_error=NULL WHERE id=?",(sys.argv[3],))\n else:c.execute(f"UPDATE {t} SET status=CASE WHEN attempts>=3 THEN 'FAILED' ELSE 'PENDING' END,last_error=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(sys.argv[5][:1000],sys.argv[3]))\n c.commit()`;
function sql(...args){return spawnSync(py,['-c',code,db,...args],{encoding:'utf8'});}
const creds=JSON.parse(await readFile('/home/ubuntu/.wechatbot/credentials.json','utf8'));const userId=creds.userId;
const bot=new WeChatBot({storage:'file',logLevel:'warn'});await bot.login({force:false});await bot.contextStore.load();
async function tick(){for(let i=0;i<10;i++){const r=sql('claim');if(r.status!==0||!r.stdout.trim())break;const x=JSON.parse(r.stdout);try{await bot.send(userId,x.message);sql('done',String(x.id),x.source);console.log(`sent ${x.source} reminder ${x.id}`)}catch(e){sql('fail',String(x.id),x.source,String(e));console.error(`failed ${x.source} reminder ${x.id}:`,e)}}}
await tick();setInterval(()=>tick().catch(console.error),15000);
for(const sig of ['SIGINT','SIGTERM'])process.on(sig,()=>{bot.stop();process.exit(0)});
