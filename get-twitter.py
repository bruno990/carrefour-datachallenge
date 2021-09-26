import json
import boto3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from decouple import config
import tweepy
import preprocessor as p
import ibm_watson
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator, IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions

st.set_page_config(page_title='Trend Topics', initial_sidebar_state = 'auto')

@st.cache
def lambda_handler():
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table('trends-twitter')
    
    
    return {
        'statusCode': 200,
        'body': table.scan()
    }
    
def get_datas(items):
    
    as_of = []
    
    for item in items:
        format_date = datetime.fromisoformat(item['as_of'][:-1]).strftime('%d/%m/%Y %H:%M:%S')
        as_of.append(format_date)
        
    return list(reversed(as_of))

def get_trends(items):
    
    trends = {}

    for item in items:
        format_date = datetime.fromisoformat(item['as_of'][:-1]).strftime('%d/%m/%Y %H:%M:%S')
        trends[format_date] = item['trends']
    
    return trends

def auth_twiter():
    
    consumer_key = config('consumer_key')
    consumer_secret = config('consumer_secret')
    access_token = config('access_token')
    access_token_secret = config('access_token_secret')
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    return api

def get_twitter(query):
    
    api = auth_twiter()
    
    tweets = []
    tweets_clean = []
    tweets_sentiments = []
    snt_results = {}
    
    st.text(f"Tweets relacionados ao termo {query['name'].values[0]}")
    results = api.search_tweets(q=query['query'].values[0], count=10, lang='pt-br')
    
    for result in results:
        tweets.append(result.text)
        
    #p.set_options(p.OPT.URL, p.OPT.EMOJI, p.OPT.ESCAPE_CHAR)
    for tweet in tweets:
        tweets_clean.append(p.clean(tweet))
    
    for tweet in tweets_clean:
        temp = busca_sentimento(tweet)
        tweets_sentiments.append(temp['sentiment']['document'])
        
    for _ in range(len(tweets)):
        snt_results[tweets[_]] = tweets_sentiments[_]
        
    df_sentiment = pd.DataFrame(snt_results).T
    df_sentiment = df_sentiment.reset_index()
    df_sentiment.columns = ['Tweet', 'Score', 'Sentimento']
    
    return df_sentiment
    
def busca_sentimento(texto):
    
    #IBM Watson
    authenticator = IAMAuthenticator(config('ibm_authenticator'))
    nlu = ibm_watson.NaturalLanguageUnderstandingV1(version='2020-09-20', authenticator=authenticator)
    nlu.set_service_url = config('ibm_url_nlu')
    
    result = nlu.analyze(text= texto, language= 'pt',
                            features=Features
                            (
                            sentiment=SentimentOptions()
                            )
                        ).get_result()
    return result
    
    
if __name__=='__main__':
    
    retorno = lambda_handler()
    datas = get_datas(retorno['body']['Items'])
    trends = get_trends(retorno['body']['Items'])
    
    # Configurações streamlit
    st.title('Trend Topics - Twitter')
    
    
    select = st.sidebar.selectbox('Selecione a data', sorted(datas, reverse=True))
    trend_select = trends[select]
    
    df_trends = pd.DataFrame(trend_select).sort_values(by=['tweet_volume', 'name'], ascending=[False, True])
    df_trends_without_none = df_trends[df_trends['tweet_volume'] > 0]
    
    graph = px.bar(df_trends_without_none, x= 'name', y='tweet_volume', labels={'tweet_volume': 'Volume', 'name': 'Topic'})
    
    st.plotly_chart(graph)
    
    st.text('Tabela com os trending topics')
    st.dataframe(df_trends.reset_index()[['name', 'tweet_volume', 'url']])
    
    select_topic = st.sidebar.selectbox('Selecione o tópico', df_trends['name'])
                                        
    df_sentiment = get_twitter(df_trends[df_trends['name'] == select_topic])
    
    st.table(df_sentiment)
    