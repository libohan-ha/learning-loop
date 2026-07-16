import tempfile,unittest
from pathlib import Path
from learning_loop import service as s
from learning_loop import review as r
from learning_loop.db import connect

class FlowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'x.db'
 def tearDown(self):self.tmp.cleanup()
 def test_full_loop_and_review(self):
  u=s.start_unit('数学','抽象逆矩阵','识别互逆关系','独立完成同类题',30,self.db)
  u=s.submit_practice(u['id'],'做题','INDEPENDENT','SUCCESS','独立完成3题',path=self.db)
  self.assertEqual(u['stage'],'EXTRACTING')
  u=s.submit_extraction(u['id'],'看到AB=E时优先想到互逆关系，再利用可逆性质变形，避免直接展开硬算。','出现AB=E时优先想到什么？',self.db)
  u=s.close_unit(u['id'],'CORE',path=self.db);self.assertEqual(u['mastery_status'],'UNTESTED')
  c=connect(self.db);c.execute("UPDATE reviews SET due_at='2000-01-01'");c.commit();c.close()
  due=r.due_reviews('数学',path=self.db);self.assertEqual(len(due),1)
  result=r.submit_review(due[0]['id'],'INDEPENDENT','INDEPENDENT',path=self.db);self.assertEqual(result['mastery_status'],'RELIABLE')
 def test_cannot_close_without_evidence(self):
  u=s.start_unit('408','红黑树插入','掌握调整','做题',30,self.db)
  with self.assertRaises(s.RuleError):s.close_unit(u['id'],'CORE',path=self.db)
 def test_one_open_per_subject(self):
  s.start_unit('英语','长难句','翻译','独立翻译',30,self.db)
  with self.assertRaises(s.RuleError):s.start_unit('英语','阅读','错因','做题',30,self.db)
 def test_ai_followup_has_destination(self):
  u=s.start_unit('408','AVL','调整','做题',30,self.db)
  s.submit_practice(u['id'],'做题','HINTED','PARTIAL','',path=self.db)
  s.submit_extraction(u['id'],'看到失衡先确定最小失衡子树，再按类型旋转并重新染色。','失衡后第一步是什么？',self.db)
  s.save_audit(u['id'],{'follow_up_question':'为什么先找最小失衡子树？','evidence_level':'GENERAL'},self.db)
  with self.assertRaises(s.RuleError):s.close_unit(u['id'],'CORE',path=self.db)
  u=s.close_unit(u['id'],'CORE','defer',path=self.db);self.assertEqual(u['mastery_status'],'FRAGILE')

if __name__=='__main__':unittest.main()
