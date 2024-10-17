import requests

class API:
    def __init__(self) -> None:
        self.base_url = "http://ru.api.openweathermap.org/data/2.5/weather"
        self.api_key = "XXX"
    
    def get_weather(self, city_name):
        request_res = requests.get(self.base_url, params={'q': city_name, 'units': 'metric', 'lang': 'ru', 'APPID': self.api_key})
        data = request_res.json()
        
        if (data['cod'] == '404'):
            return None
        
        try:
            weather_description = f'''
            Погода по вашему запросу:
            Город: {data['name']}
            
            {data['weather'][0]['description']}

            Температура: {data['main']['temp']} ощущается как {data['main']['feels_like']}
            Температура минимальная: {data['main']['temp_min']},
            Температура максимальная: {data['main']['temp_max']},

            Давление: {data['main']['pressure']} мм рт.ст,
            Влажность: {data['main']['humidity']}%,
            '''
            return weather_description
        except:
            return None
        
    def validate_city(self, city_name):
        request_res = requests.get(self.base_url, params={'q': city_name, 'units': 'metric', 'lang': 'ru', 'APPID': self.api_key})
        data = request_res.json()
        
        if (data['cod'] == '404'):
            return False
        
        try:
            return True
        except:
            return False
