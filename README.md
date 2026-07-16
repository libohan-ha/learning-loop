# Learning Loop（学习闭环）

一个只服务个人考研的证据驱动学习流程执行器。它不以学习时长或笔记数量判定成功，而是强制完成：**独立实践 → 自己的话提炼 → 延迟提取与应用测试**。

## 功能

- 数学、408、英语、政治的独立活动单元
- 时间护栏检查点，而非计时绩效
- 实践证据与自己的话提炼
- 流程状态与掌握状态分离
- 短期、题型轮次、长期三层复盘
- 提取与应用双证据
- Pi Agent Skill 审核
- React 手机优先面板
- 七天实验统计

## 本地开发

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
export LEARNING_LOOP_DB=$PWD/data/learning_loop.db
uvicorn learning_loop.api:app --host 127.0.0.1 --port 18120
```

```sh
cd frontend
npm install
npm run dev
```

## CLI

```sh
learning-loop init
learning-loop start 数学 "抽象逆矩阵" --objective "识别互逆关系" --practice "独立完成同类题" --guard 60
learning-loop dashboard
learning-loop due 数学
```

## 数据与安全

运行数据库必须保存在仓库外或 `data/` 中，不提交 Git。公网部署必须设置 `LEARNING_LOOP_TOKEN`；后端建议仅监听 `127.0.0.1`，由受保护的前端代理访问。

## License

MIT
