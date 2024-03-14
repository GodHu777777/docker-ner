# choose light python 
FROM python:3.8-slim
WORKDIR /app

# COPY from ... to ... 
COPY requirements.txt /app
COPY run_ner.py /app
COPY run.sh /app
COPY app.py /app

# install relative libraries 
# "--no-cache-dir" can lower storage usage 
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask


RUN ./run.sh

# RUN python pred.py

RUN flask --app app run