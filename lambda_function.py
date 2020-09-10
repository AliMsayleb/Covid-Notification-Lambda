import boto3
import json
import os
import urllib3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

SENDER = os.environ['SENDER_NAME'] + "<" + os.environ['SENDER_EMAIL'] +">"
RECIPIENTS = json.loads(os.environ['RECEPIENT_EMAILS'])
ses_client = boto3.client('ses')
sqs_client = boto3.client('sqs')
CHARSET = "UTF-8"
RETRIES_LIMIT = 3
DELAY_TIME = 900

def lambda_handler(event, context):
    try:
        new_cases = get_covid_new_cases()
    except:
        retry_later(event)
        return

    date_yesterday = (datetime.today() - timedelta(days = 1)).strftime("%A %d-%B-%Y")
    SUBJECT = "Covid cases update: " + date_yesterday
    BODY_TEXT = str(new_cases) + " confirmed new covid cases on " + date_yesterday + '.'
    BODY_HTML = "<h2>" + str(new_cases) + " confirmed new covid cases on " + date_yesterday + '.</h2>'
    
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': RECIPIENTS,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
def get_covid_new_cases():
    http = urllib3.PoolManager()
    response = http.request('GET', build_covid_resource_url()).data
    response_object = json.loads(response.decode('utf-8'))
    if len(response_object) != 2 or response_object[1]['Cases'] - response_object[0]['Cases'] < 0: # Corrupted data from the resource API
        print(response_object)
        raise "Incorrect response" # Raising exception to retry later
        
    return response_object[1]['Cases'] - response_object[0]['Cases']
    
def build_covid_resource_url():
    today = datetime.today()
    two_days_ago = today - timedelta(days = 2)
    one_day_ago = today - timedelta(days = 1)
    one_day_ago = one_day_ago.timetuple()
    two_days_ago = two_days_ago.timetuple()
    base_url = 'https://api.covid19api.com/country/' + os.environ['COUNTRY'] + '/status/confirmed'
    from_year = append_zero_if_needed(two_days_ago.tm_year)
    from_month = append_zero_if_needed(two_days_ago.tm_mon)
    from_day = append_zero_if_needed(two_days_ago.tm_mday)
    to_year = append_zero_if_needed(one_day_ago.tm_year)
    to_month = append_zero_if_needed(one_day_ago.tm_mon)
    to_day = append_zero_if_needed(one_day_ago.tm_mday)
    from_date = from_year + '-' + from_month + '-' + from_day + 'T00:00:00Z'
    to_date = to_year + '-' + to_month + '-' + to_day + 'T00:00:00Z'
    
    return base_url + '?from=' + from_date + '&to=' + to_date
    
def append_zero_if_needed(num):
    if num < 10:
        return '0' + str(num)
        
    return str(num)
    
def retry_later(event):
    try: # get the number of retries from the sqs queue
        num = int(event['Records'][0]['body'])
        num = num + 1
    except: # Not triggered by SQS (first time will be triggered by cloudwatch)
        num = 1
    if num >= RETRIES_LIMIT:
        print ("Retries limit number reached")
        return
    resp = sqs_client.send_message(QueueUrl=os.environ['RETRY_QUEUE_URL'], MessageBody=str(num), DelaySeconds=DELAY_TIME)
