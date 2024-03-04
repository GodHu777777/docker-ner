# choose light python 
FROM python:3.8-slim
WORKDIR /app

# COPY from ... to ... 
COPY requirements.txt /app
COPY run_ner.py /app
COPY run.sh /app

# install relative libraries 
# "--no-cache-dir" can lower storage usage 
RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT ["/app/run.sh"]