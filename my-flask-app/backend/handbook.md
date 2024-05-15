# 持续运行flask(App.py) 并把log和输出保存在your_log_file.out

```bash
gunicorn -w 4 -b 0.0.0.0:80 App:app --access-logfile - | tee your_log_file.out
```