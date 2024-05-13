# choose light python 
FROM genghonghu/python:v0.1
WORKDIR /app

RUN mkdir -p /tmp/test-ner

# COPY from ... to ... 
COPY requirements.txt /app

# COPY model 
COPY /test-ner/* /tmp/test-ner

# RUN python pred.py

CMD python3 app.py