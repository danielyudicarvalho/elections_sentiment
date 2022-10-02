import re
import string

import snscrape.modules.twitter as sns
import spacy
from joblib import dump, load
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

converter  = SentenceTransformer ( 'multi-qa-distilbert-cos-v1' )

model_final = load('eleicoes.joblib')

result = model_final.predict([converter.encode('O que é eleição?')])
print(result)


class Predictor:
    def __init__(self):
        self.model = load('eleicoes.joblib')
        self.converter = SentenceTransformer('multi-qa-distilbert-cos-v1')
        self.nlp = spacy.load('pt_core_news_sm')
        self.stopwords = spacy.lang.pt.stop_words.STOP_WORDS
        
        
    def preprocessor(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r"https?://[A-Za-z0-9./]+",' ', text)
        text = re.sub(r" +", ' ', text)
        documento = self.nlp(text)
        lista = []
        for token in documento:
            lista.append(token.lemma_)
        lista = [palavra for palavra in lista if palavra not in self.stopwords and palavra not in string.punctuation]
        lista = ' '.join([str(elemento) for elemento in lista if not elemento.isdigit()])
        return lista

    def predict(self, payload):
        return self.model.predict([self.converter.encode(self.preprocessor(payload))])

def init_db():
    client = MongoClient('mongodb://mongo:27017/')
    db = client.get_database('twitter')
    eleicoes = db.get_collection('eleicoes')
    return eleicoes


if '__main__' == __name__:
    predictor = Predictor()
    eleicoes = init_db()
    while True:
        query = "(Lula OR lula OR Ciro OR Bolsonaro OR bolsonaro OR Simone OR simone OR soraya OR Tebet OR Soraya OR Padre Kelmom OR eleições OR debate OR davilla OR D'ávilla OR Davilla) lang:pt"
        max_size = 200
        for tweet in sns.TwitterSearchScraper(query).get_items():
            res = predictor.predict(tweet.content)
            res = res.tolist()
            res = res[0]
            if len(re.findall('bolsonaro',tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'bolsonaro'}},upsert=True)
            if len(re.findall('ciro',tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'ciro'}},upsert=True)
            if len(re.findall('lula',tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'lula'}},upsert=True)
            if len(re.findall('simone | tebet',tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'tebet'}},upsert=True)
            if len(re.findall('soraya',tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'soraya'}},upsert=True)
            if len(re.findall('kelmon | padre',tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'kelmon'}},upsert=True)
            if len(re.findall("davilla | d'ávilla",tweet.content, re.IGNORECASE)) > 0:
                eleicoes.update_one({'id':tweet.id,'tweet':tweet.content},{'$set':{'date':tweet.date,'tweet':tweet.content,'sentiment':res, 'candidate':'davilla'}},upsert=True)
