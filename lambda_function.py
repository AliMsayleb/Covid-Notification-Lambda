import boto3
import json
import os
import urllib3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

SENDER = os.environ['SENDER_NAME'] + "<" + os.environ['SENDER_EMAIL'] +">"
RECIPIENT = os.environ['RECEPIENT_EMAIL']
client = boto3.client('ses',region_name=os.environ['AWS_SES_REGION'])
CHARSET = "UTF-8"

def lambda_handler(event, context):
    response = get_covid_new_cases()
    response_object = json.loads(response.decode('utf-8'))
    new_cases = (response_object[1]['Cases'] - response_object[0]['Cases'])
    date_yesterday = (datetime.today() - timedelta(days = 1)).strftime("%A %d-%B-%Y")
    SUBJECT = "Covid cases update: " + date_yesterday
    BODY_TEXT = str(new_cases) + " confirmed new covid cases on " + date_yesterday + '.'
    BODY_HTML = "<h2>" + str(new_cases) + " confirmed new covid cases on " + date_yesterday + '.</h2>'
    
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
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
    response = http.request('GET', build_covid_resource_url())
    
    return response.data
    
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
