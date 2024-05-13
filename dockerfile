# choose light python 
FROM genghonghu/python-nlp:v1.0
WORKDIR /app

RUN mkdir -p /tmp/test-ner

# COPY from ... to ... 
COPY requirements.txt /app
COPY pod.py /app

# COPY model 
COPY /test-ner/* /tmp/test-ner

# RUN python pred.py

CMD python3 pod.py