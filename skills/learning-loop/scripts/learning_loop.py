#!/usr/bin/env python3
import os,sys
ROOT=os.getenv('LEARNING_LOOP_ROOT','/home/ubuntu/learning-loop')
sys.path.insert(0,os.path.join(ROOT,'src'))
os.environ.setdefault('LEARNING_LOOP_DB','/home/ubuntu/learning-loop-data/learning_loop.db')
from learning_loop.cli import main
raise SystemExit(main())
