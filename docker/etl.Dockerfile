FROM python:3.7

WORKDIR /app

COPY app/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
RUN python -m spacy download pt_core_news_sm

COPY app/etl.py .
COPY model/eleicoes.joblib .

ENTRYPOINT ["python3", "etl.py"]

