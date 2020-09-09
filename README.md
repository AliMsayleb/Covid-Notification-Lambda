# Covid Daily Notification Email via AWS Lambda

This is the aws lambda code for sending a daily email with the covid updates
It is made for lambda with runtime Python 3.8 although it probably supports other versions of python
You can setup a recipient email and a certain time to receive daily updates to this email regarding the new covid number of confirmed cases.

## AWS Technologies Used
 - Lambda function (runtime of python 3.8)
 - Simple email service SES for sending emails
 - CloudWatch for cron job (triggering the lambda function at a certain time of the day)

## Setup
 - First you need to create a lambda function with runtime of python 3.8
 - After function creation go to permissions, role, policies and attach SES full policy for the lambda role
 - Now open AWS Simple Email Service SES and add your email and verify it (in Sandbox mode you probably need to verify the email receiver as well)
 - Now go to CloudWatch and click on rules to create a new rule; select schedule and add the following cron expression `30 10 * * ? *` This tells the cron to trigger your lambda function every day at 10:30 AM UTC timezone. Then add a target your lambda function. Proceed and save the rule
 - Now back to your lambda function, copy paste the code from [lambda_function.py](https://github.com/AliMsayleb/Covid-Notification-Lambda/blob/master/lambda_function.py) into your lambda function 
 - Add the environment variables below the lambda function code:
   - `COUNTRY`: the country that you want the daily results for.
   - `AWS_SES_REGION`: the aws region that you're using for SES (you can see it in the url).
   - `SENDER_NAME`: the name of the sender that you want to set for when you receive an email.
   - `SENDER_EMAIL`: the email of the sender that you verified in the SES section.
   - `RECEPIENT_EMAIL`: the email of the person you want to send this email to.
 - Save the function from the top right of the page and click on test, and trigger an event manually. At this stage you should receive an email at the time when you triggered the email, and the daily email cron will be working as well.

## Notes

In case you want to send a daily update for multiple recipients, you can hardcode them in the lambda code, or you can just add a json decode to `RECEPIENT_EMAIl` and then pass all the recipients from the environment variable as a json string
