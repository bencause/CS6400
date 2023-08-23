from slack_sdk.webhook import WebhookClient
import os
import pandas as pd
from datetime import datetime, timedelta
import pytz

#slack_thread set up
webhook_url = os.environ['CUSTOM_SLACK_WEBHOOK_URL']
client = WebhookClient(webhook_url)
#timezone
eastern = pytz.timezone('US/Eastern')

def get_close_events(x_days):
    df = pd.read_csv('cs6400.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%a %b %d, %Y').dt.tz_localize(eastern)
    current_date_us_east = datetime.now(eastern)
    df['date_difference'] = (df['Date'] - current_date_us_east).dt.days
    dates_within_x_days = df[df['date_difference'].between(0, x_days)]
    dates_within_x_days['Details'] = dates_within_x_days['Details'].str.replace('Calendar Event', '')
    dates_within_x_days = dates_within_x_days.rename(columns={'Due': 'Due_Time', 'date_difference': 'Due_in_x_days', 'Date':'Due_date'})
    dates_within_x_days['Due_date'] = dates_within_x_days['Due_date'].dt.strftime('%Y-%m-%d')
    return dates_within_x_days[['Details','Due_date','Due_in_x_days','Due_Time']]


def slack_thread(df):
    alert_text = f"""
        :crannounce: `CS6400 events notification` : `Incoming events within 7 days` :crannounce: 
        (Source : pending_this is just test)
        ```{df.to_markdown()}```
        """
    return alert_text


def main():
    df = get_close_events(7)
    if df.empty:
        print("All on-track, not events incoming")
    else:
        report = slack_thread(df)
        api_response = client.send(
            text=report
        )


if __name__ == '__main__':
    main()