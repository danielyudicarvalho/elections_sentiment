import datetime
import time
from random import randint

import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient

st.set_page_config(
        page_title="Analise de sentimentos de tweets dos candidatos a presidência",
        page_icon="✅",
        layout="wide",
)

def init_db():
    client =client = MongoClient('mongodb://mongo:27017/')
    db = client.get_database('twitter')
    eleicoes = db.get_collection('eleicoes')
    return eleicoes

class Dashboard:
    def __init__(self):
        self.eleicoes = init_db()
    
    def get_tweets_by_candidate(self, candidate):
        total = len(list(self.eleicoes.find({'candidate': candidate})))
        pos = len(list(self.eleicoes.find({'candidate': candidate, 'sentiment': 'pos'})))
        neg = len(list(self.eleicoes.find({'candidate': candidate, 'sentiment': 'neg'})))
        
        return total, pos, neg
    
    def plot_sentiment_dashboard(self):
        st.title('Dashboard de Sentimentos')
        st.write('Aqui você pode ver o número de tweets positivos e negativos de cada candidato')
        total, pos, neg = self.get_tweets_by_candidate('bolsonaro')
        st.write(f'Bolsonaro: {total} tweets, {pos} positivos e {neg} negativos')
        total, pos, neg = self.get_tweets_by_candidate('ciro')
        st.write(f'Ciro: {total} tweets, {pos} positivos e {neg} negativos')
        total, pos, neg = self.get_tweets_by_candidate('lula')
        st.write(f'Lula: {total} tweets, {pos} positivos e {neg} negativos')
        total, pos, neg = self.get_tweets_by_candidate('tebet')
        st.write(f'Simone Tebet: {total} tweets, {pos} positivos e {neg} negativos')
        total, pos, neg = self.get_tweets_by_candidate('davilla')
        st.write(f'Davilla: {total} tweets, {pos} positivos e {neg} negativos')
        total, pos, neg = self.get_tweets_by_candidate('soraya')
        st.write(f'Soraya: {total} tweets, {pos} positivos e {neg} negativos')
        total, pos, neg = self.get_tweets_by_candidate('kelmon')
        st.write(f'Padre Kelmon: {total} tweets, {pos} positivos e {neg} negativos')

    
    def return_negative_from_60_minutes_ago(self,candidate):
        result = []
        for i in range(1,60,5):
                res = self.eleicoes.find({'candidate': candidate,'sentiment':'neg','date': {'$gte': datetime.datetime.now() - datetime.timedelta(minutes=i+5),'$lt': datetime.datetime.now() - datetime.timedelta(minutes=i)}})
                result.append(len(list(res)))
        return result

    def return_positive_from_60_minutes_ago(self,candidate):
        result = []
        for i in range(1,60,5):
                res = self.eleicoes.find({'candidate': candidate,'sentiment':'pos','date': {'$gte': datetime.datetime.now() - datetime.timedelta(minutes=i+5),'$lt': datetime.datetime.now() - datetime.timedelta(minutes=i)}})
                result.append(len(list(res)))
        return result
    
    def return_neutral_from_60_minutes_ago(self,candidate):
        result = []
        for i in range(1,60,5):
                res = self.eleicoes.find({'candidate': candidate,'sentiment':'neu','date': {'$gte': datetime.datetime.now() - datetime.timedelta(minutes=i+5),'$lt': datetime.datetime.now() - datetime.timedelta(minutes=i)}})
                result.append(len(list(res)))
        return result
    
    def return_total_from_60_minutes_ago(self,candidate):
        result = []
        for i in range(1,60,5):
            res = self.eleicoes.find({'candidate': candidate,'date': {'$gte': datetime.datetime.now() - datetime.timedelta(minutes=i+5),'$lt': datetime.datetime.now() - datetime.timedelta(minutes=i)}})
            result.append(len(list(res)))
        return result
    
    

dashboard = Dashboard()
placeholder = st.empty()
candidatos = ['bolsonaro','ciro','davilla','kelmon','lula','soraya','tebet']   

while True:
    panda1 = pd.DataFrame()
    panda2 = pd.DataFrame()
    panda3 = pd.DataFrame()
    panda = pd.DataFrame(list(dashboard.eleicoes.find({},{'_id':0,'sentiment':0}).sort('date', -1).limit(100)))
    dates = [datetime.datetime.now() - datetime.timedelta(minutes=i) for i in range(1,60,5)]
    panda1['date'] = dates
    panda2['date'] = dates
    panda3['date'] = dates
    
    
    with placeholder.container():
        st.markdown("### Total de tweets por candidato")
        for candidato in candidatos:
            total = dashboard.return_total_from_60_minutes_ago(candidato)
            panda3[candidato] = total
        st.area_chart(panda3, x="date", y=candidatos)
        
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            for candidato in candidatos:
                total = dashboard.return_negative_from_60_minutes_ago(candidato)
                panda1[candidato] = total
            st.markdown("### Negativos por candidato")
            st.line_chart(panda1, x="date", y=candidatos)
                
        with fig_col2:
            for candidato in candidatos:
                    total = dashboard.return_positive_from_60_minutes_ago(candidato)
                    panda2[candidato] = total

            st.markdown("### Positivos por candidato")
            st.line_chart(panda2, x="date", y=candidatos)
            

        job_filter = st.selectbox("Selecione o candidato", candidatos, key=randint(0,1000))
        if job_filter not in candidatos:
            job_filter = 'bolsonaro'
        df = pd.DataFrame()
        df['date'] = [datetime.datetime.now() - datetime.timedelta(minutes=i) for i in range(1,60,5)]
        df['neg'] = dashboard.return_negative_from_60_minutes_ago(job_filter)
        df['neu'] = dashboard.return_neutral_from_60_minutes_ago(job_filter)
        df['pos'] = dashboard.return_positive_from_60_minutes_ago(job_filter)
        st.markdown("### Sentimentos por candidato")
        st.write(job_filter)
        st.bar_chart(df, x="date", y=['neg','neu','pos'])
            
        st.markdown("### Tweets")
        st.dataframe(panda)
        time.sleep(10)
        
        
        