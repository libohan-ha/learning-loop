import os, sqlite3
from pathlib import Path

SCHEMA_VERSION=1

def db_path():
    return Path(os.getenv("LEARNING_LOOP_DB","data/learning_loop.db")).expanduser()

def connect(path=None):
    p=Path(path) if path else db_path(); p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p); c.row_factory=sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON"); c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA busy_timeout=5000")
    return c

def init_db(path=None):
    c=connect(path)
    c.executescript('''
CREATE TABLE IF NOT EXISTS units(
 id INTEGER PRIMARY KEY, subject TEXT NOT NULL CHECK(subject IN ('数学','408','英语','政治')),
 title TEXT NOT NULL, objective TEXT NOT NULL, practice_plan TEXT NOT NULL, guard_minutes INTEGER NOT NULL DEFAULT 60,
 guard_due_at TEXT, guard_extensions INTEGER NOT NULL DEFAULT 0,
 flow_status TEXT NOT NULL DEFAULT 'ACTIVE', stage TEXT NOT NULL DEFAULT 'UNDERSTANDING', mastery_status TEXT NOT NULL DEFAULT 'UNTESTED',
 importance TEXT NOT NULL DEFAULT 'NORMAL', current_position TEXT, blocker TEXT, next_action TEXT,
 practice_type TEXT, independence TEXT, practice_result TEXT, practice_note TEXT, practice_metrics TEXT,
 extraction TEXT, follow_up_question TEXT, follow_up_status TEXT, skip_reason TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, closed_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_open_unit_per_subject ON units(subject) WHERE flow_status IN ('ACTIVE','PENDING');
CREATE TABLE IF NOT EXISTS extraction_versions(id INTEGER PRIMARY KEY,unit_id INTEGER NOT NULL,content TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(unit_id) REFERENCES units(id));
CREATE TABLE IF NOT EXISTS review_prompts(id INTEGER PRIMARY KEY,unit_id INTEGER NOT NULL,question TEXT NOT NULL,answer TEXT,kind TEXT NOT NULL DEFAULT 'RECALL',active INTEGER NOT NULL DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(unit_id) REFERENCES units(id));
CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,unit_id INTEGER NOT NULL,pool TEXT NOT NULL,due_at TEXT,round_name TEXT,priority INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL DEFAULT 'QUEUED',recall_result TEXT,application_result TEXT,note TEXT,reviewed_at TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(unit_id) REFERENCES units(id));
CREATE TABLE IF NOT EXISTS audits(id INTEGER PRIMARY KEY,unit_id INTEGER NOT NULL,provider TEXT,model TEXT,verdict TEXT,possible_error TEXT,key_gap TEXT,follow_up_question TEXT,importance_suggestion TEXT,mastery_suggestion TEXT,evidence_level TEXT NOT NULL DEFAULT 'NONE',raw_json TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(unit_id) REFERENCES units(id));
CREATE TABLE IF NOT EXISTS subject_entries(id INTEGER PRIMARY KEY,subject TEXT NOT NULL,action TEXT NOT NULL,reason TEXT,batch_size INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS friction_logs(id INTEGER PRIMARY KEY,day TEXT NOT NULL DEFAULT (date('now','localtime')),content TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY,unit_id INTEGER NOT NULL,kind TEXT NOT NULL DEFAULT 'GUARD',due_at TEXT NOT NULL,message TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PENDING',attempts INTEGER NOT NULL DEFAULT 0,last_error TEXT,sent_at TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(unit_id) REFERENCES units(id));
CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(status,due_at);
CREATE TABLE IF NOT EXISTS general_reminders(id INTEGER PRIMARY KEY,due_at TEXT NOT NULL,message TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PENDING',attempts INTEGER NOT NULL DEFAULT 0,last_error TEXT,sent_at TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_general_reminders_due ON general_reminders(status,due_at);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,entity_type TEXT NOT NULL,entity_id INTEGER,action TEXT NOT NULL,payload TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
PRAGMA user_version=1;
''')
    c.commit(); c.close()
