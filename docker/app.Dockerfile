FROM python:3.7

WORKDIR /app

COPY app/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8501

COPY app/app.py .

ENTRYPOINT ["streamlit", "run"]

CMD ["app.py"]