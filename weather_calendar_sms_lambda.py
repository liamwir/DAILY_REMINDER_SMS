import base64
import json
import os
import urllib
from urllib import request, parse
from datetime import datetime

DATE_FORMAT = '%A, %B %d, %Y'

MY_WEATHER_URL = 'https://api.weather.gov/gridpoints/TAE/82,86/forecast'
MY_CALENDAR_URL = 'https://h0jsu5huz6.execute-api.us-east-1.amazonaws.com/dev/events/all'

TWILIO_SMS_URL = 'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

MY_PHONE_NUMBER='+19048599457'
TWILIO_PHONE_NUMBER='+18455721218'
def get_weather_data() -> str:
    
    print("sending weather forecast request")
    with urllib.request.urlopen(MY_WEATHER_URL) as response:
        status = response.getcode()
        if status == 200:
            data = json.load(response)

    if status == 200:
        print("Received response with weather data")
        current_weather = data["properties"]["periods"][0]
        temp = current_weather["temperature"]
        wind = current_weather["windSpeed"]
        forecast = current_weather["shortForecast"]
        date_obj = datetime.fromisoformat(current_weather["startTime"]) #2022-05-31T06:00:00-04:00
        date = date_obj.strftime(DATE_FORMAT)

        weather_data = f"Forecast and Schedule for {date}: \n \n* {forecast} \n* Temperature: {temp}\N{DEGREE SIGN} \n* Wind Speed: {wind}"
        print(weather_data)
        return weather_data

    else:
        print(f"unexpected status code = {status}")
        return f"Unable to get weather data due to the unexpected status code: {status}"


def get_calendar_data() -> str:
    
    print("sending calendar info request")
    with urllib.request.urlopen(MY_CALENDAR_URL) as response:
        status = response.getcode()
        if status == 200:
            data = response.read().decode('utf-8')

    if status == 200:
        print("Received response with calendar data")
        calendar_data = data
        print(calendar_data)

        return calendar_data

    else:
        print(f"unexpected status code = {status}")
        return f"Unable to get calendar data due to the unexpected status code: {status}"
    

def send_SMS(text_data):
    print("Creating SMS request")
    to_number = MY_PHONE_NUMBER
    from_number = TWILIO_PHONE_NUMBER
    body = text_data

    if not TWILIO_ACCOUNT_SID:
        return "Unable to access Twilio Account SID."
    elif not TWILIO_AUTH_TOKEN:
        return "Unable to access Twilio Auth Token."
    elif not to_number:
        return "The function needs a 'To' number in the format +12023351493"
    elif not from_number:
        return "The function needs a 'From' number in the format +19732644156"
    elif not body:
        return "The function needs a 'Body' message to send."

    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)
    post_params = {"To": to_number, "From": from_number, "Body": body}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        print("Sending SMS")
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e

    return "SMS sent successfully!"


def lambda_handler(event, context):   
    weather_data = get_weather_data()
    calendar_data = get_calendar_data()

    response_text = f'{weather_data}\n{calendar_data}' 
    status = send_SMS(response_text)
    return status
    