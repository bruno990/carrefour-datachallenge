import json
import tweepy
import os
import boto3

def trends(event, context):
    
    #Autenticações
    consumer_key = os.environ['consumer_key']
    consumer_secret = os.environ['consumer_secret']
    access_token = os.environ['access_token']
    access_token_secret = os.environ['access_token_secret']
    BRAZIL_WOE_ID = 23424768
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    brazil_trends = api.trends_place(BRAZIL_WOE_ID)
 
    trends = json.loads(json.dumps(brazil_trends, indent=1))
    
    response = load_trends(trends[0])
    
    return {
        'statusCode': 200,
        'body': trends[0]['as_of']
    }
    
def load_trends(trends):
    
    dynamodb = boto3.resource('dynamodb')
    
    #create_table()
    
    table = dynamodb.Table('trends-twitter')
    
    #created_at = trends['created_at']
    #print(f'Item adicionada {created_at}')
    response = table.put_item(Item=trends)
    
    return response
