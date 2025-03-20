import openai
import requests
import smtplib
from email.mime.text import MIMEText
import os
import getLocAndCity
from datetime import datetime, timezone, timedelta

#Keys saved as environment variables for user on local computer. Can insert your own keys here

#OpenAI API key; Can obtain your own via https://platform.openai.com/api-keys
#Account must be authorized to access models even if you have your own key (key: free ; access: paid)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

#OpenWeatherMapAPI key, obtained through https://openweathermap.org/
weather_api_key = os.getenv("WEATHER_API_KEY")
if not weather_api_key:
    raise ValueError("WEATHER_API_KEY environment variable is not set")

#Code configured for gmail, need key to allow access via "App Passwords": https://myaccount.google.com/apppasswords
smtp_api_key = os.getenv("SMTP_API_KEY")
if not smtp_api_key:
    raise ValueError("SMTP_API_KEY environment variable is not set")

def get_weather(city):
    # OpenWeatherMap endpoints
    current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={weather_api_key}&units=metric"

    #Fetch current weather
    current_response = requests.get(current_weather_url)
    if current_response.status_code == 200:
        current_data = current_response.json()
        current_temp = current_data['main']['temp']
        current_humidity = current_data['main']['humidity']
        current_wind_speed = current_data['wind']['speed']
        description = current_data['weather'][0]['description']
    else:
        return "Unable to fetch current weather data."

    #Fetch forecast data
    forecast_response = requests.get(forecast_url)
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()

        # Get today's UTC date and tomorrow's start
        today = datetime.now(timezone.utc).date()
        tomorrow = today + timedelta(days=1)

        # Extract forecasts for the rest of today
        today_forecasts = [
            forecast for forecast in forecast_data['list']
            if today <= datetime.fromtimestamp(forecast['dt'], timezone.utc).date() < tomorrow
        ]

        if not today_forecasts:
            return (
                f"Today's weather in {city}:\n"
                f"- Current Temperature: {current_temp:.1f}°C\n"
                f"- Humidity: {current_humidity}%\n"
                f"- Wind Speed: {current_wind_speed} m/s\n"
                f"- No additional forecasts available for today.\n"
                f"- General Conditions: {description.capitalize()}"
            )

        # Extract data for summaries
        temperatures = [forecast['main']['temp'] for forecast in today_forecasts]
        humidities = [forecast['main']['humidity'] for forecast in today_forecasts]
        wind_speeds = [forecast['wind']['speed'] for forecast in today_forecasts]
        precipitation = [
            forecast.get('rain', {}).get('3h', 0) + forecast.get('snow', {}).get('3h', 0)
            for forecast in today_forecasts
        ]

        avg_temp = sum(temperatures) / len(temperatures)
        avg_humidity = sum(humidities) / len(humidities)
        avg_wind_speed = sum(wind_speeds) / len(wind_speeds)
        total_precipitation = sum(precipitation)

        summary = (
            f"Today's weather in {city}:\n"
            f"- Current Temperature: {current_temp:.1f}°C\n"
            f"- Average Temperature: {avg_temp:.1f}°C\n"
            f"- Humidity: {avg_humidity:.1f}%\n"
            f"- Wind Speed: {avg_wind_speed:.1f} m/s\n"
            f"- Total Precipitation: {total_precipitation:.1f} mm\n"
            f"- General Conditions: {description.capitalize()}"
        )
        return summary  
    else:
        return "Unable to fetch forecast data."

def ask_chatgpt(question, context):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a kind, thoughtful, caring assistant."},
            {"role": "user", "content": context + "\n" + question}
        ]
    )
    return response['choices'][0]['message']['content']


    
def send_email(provider, phonenumber):
    # Gmail account credentials, this is the sender
    email_user = '1Chasebaker@gmail.com'  
    email_password = smtp_api_key  
    

    gatewaysuffix = ""    

    # Check carrier of recipient and set the MMS gateway suffix
    if provider == "Verizon":
        gatewaysuffix = "vzwpix.com"
    elif provider == "T-Mobile":
        gatewaysuffix = "tmomail.net"
    elif provider == "AT&T":
        gatewaysuffix = "mms.att.net"
    elif provider == "Sprint":
        gatewaysuffix = "pm.sprint.com"
    elif provider == "Boost Mobile":
        gatewaysuffix = "myboostmobile.com"
    elif provider == "Cricket":
        gatewaysuffix = "mms.cricketwireless.net"
    elif provider == "Virgin Mobile":
        gatewaysuffix = "vmpix.com"
    elif provider == "US Cellular":
        gatewaysuffix = "mms.uscc.net"
    else:
        gatewaysuffix = "unknown"
        print("Carrier not recognized. Please check the provider name.")

   

    phone_number = phonenumber  
    carrier_gateway = f'{phone_number}@{gatewaysuffix}'
    
 
    subject = 'Good Morning!'
    body = response

    # Create the email
    msg = MIMEText(body)
    msg['From'] = email_user
    msg['To'] = carrier_gateway
    msg['Subject'] = subject

    # Send the email via Gmail's SMTP server

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(email_user, carrier_gateway, msg.as_string())
        print("Message sent!")
    except Exception as e:
        print(f"Error: {e}")




if __name__ == "__main__":
    #For more tailored output
    female = "Woman"
    male = "Man"
    other = ""
    #API charges by input & output tokens. If using non-local version, can shorten question template to reduce cost-per-call
    questiontemplate = "Good morning! I am a {gender} named {name}, Based on the weather, give me an idea of what I should expect through the day, and an outfit idea. Be caring and considerate of me. I am about to start my day. Give me motivation. Assume I do not know any of the weather information I am giving you."


    #Weather by location of user, if signed in and authenticated with pyicloud package. See getLocAndCity for more details.
    city = getLocAndCity.main()
    weather_info = get_weather(city)
    name = "your_name_here"
    number = "your_number_here"
    #See send_email method, gateway suffix portion for viable inputs of provider
    provider = "your_provider_here"
    #Adjust gender parameter accordingly 
    question = questiontemplate.format(gender=male, name=name)
    response = ask_chatgpt(question, weather_info)
    print(response)
    send_email(provider, number)

    #Calling for user not signed in with pyicloud
    #manually input city / zip / etc.
    city = "78208"
    weather_info = get_weather(city)
    name = "your_name_here"
    number = 'your_number_here'
    provider = "your_provider_here"
    
    question = questiontemplate.format(gender=male, name=name)
    response = ask_chatgpt(question, weather_info)
    print(response)
    send_email(provider, number)







