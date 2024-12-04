import requests
from flask import Flask, render_template, request
from markupsafe import Markup

api_key = '4e2fdebb1db241784684704a13c94a17'

def test(): # функция для теста работы api
    city_name = "Moscow"  # Замените на нужный город
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=ru"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"Город: {data['name']}")
        print(f"Температура: {data['main']['temp']}°C")
        print(f"Описание: {data['weather'][0]['description']}")
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")

test()

def check_bad_weather(conditions): # возвращает true если хорошие условия и false иначе
    result = True # также возвращает причину плохой погоды
    reasons = []
    if conditions['temperature'] < -5 or conditions['temperature'] > 35:
        result = False
        reasons += ['temperature']
    if 70 < conditions['humidity'] or conditions['humidity'] < 20:
        result = False
        reasons += ['humidity']
    if conditions['wind_speed'] > 50:
        result = False
        reasons += ['wind_speed']
    if conditions['pop'] >= 70:
        result = False
        reasons += ['pop']
    return result, reasons

app = Flask(__name__, template_folder='C:\\Users\\garry\\PycharmProjects\\WeatherProject\\templates')
@app.route('/')
def home():
    return render_template('home.html')

def get_cord(city): # (lat,lon) по названию города
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latitude = data['coord']['lat']  # Извлекаем широту
        longitude = data['coord']['lon']  # Извлекаем долготу
        return latitude, longitude
    else:
        print("Ошибка:", response.status_code, response.json())
        return None, None

@app.route('/submit', methods=['POST'])
def submit():
    start = request.form['startPoint']  # Получаем данные из формы
    end = request.form['endPoint']

    lat_start, lon_start = get_cord(start) # получаем координаты городов
    lat_end, lon_end = get_cord(end)
    url1 = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat_start}&lon={lon_start}&exclude=current,hourly&appid={api_key}'
    url2 = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat_end}&lon={lon_end}&exclude=current,hourly&appid={api_key}'
    # вероятность осадков храниться в другом api запросе
    # url_p_1 = f'https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={lat_start}&lon={lon_start}&appid={api_key}'
    # url_p_2 = f'https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={lat_end}&lon={lon_end}&appid={api_key}'

    response_start = requests.get(url1) # делаем запрос к api openweather
    print(1)
    response_end = requests.get(url2)
    print(2)
    # response_p_start = requests.get(url_p_1)  # делаем запрос к api openweather
    # response_p_end = requests.get(url_p_2)
    if response_start.status_code == 200 and response_end.status_code == 200:
        weather_start = response_start.json()
        weather_end = response_end.json()
        #
        # weather_p_start = response_p_start.json()
        # weather_p_end = response_p_end.json()

        # Извлечение нужной информации о погоде
        weather_info_start = {
            "temperature": weather_start['current']['temp'],  # Температура
            "humidity": weather_start['current']['humidity'],  # Влажность
            "wind_speed": weather_start['current']['wind_speed'],  # Скорость ветра
            "pop": weather_start['hourly'][0]['pop'] * 100,  # Вероятность осадков (умножаем на 100 для процента)
        }
        print(weather_info_start)
        weather_info_end = {
            "temperature": weather_end['current']['temp'],  # Температура
            "humidity": weather_end['current']['humidity'],  # Влажность
            "wind_speed": weather_end['current']['wind_speed'],  # Скорость ветра
            "pop": weather_end['hourly'][0]['pop'] * 100,  # Вероятность осадков (умножаем на 100 для процента)
        }

        weather_states = {
            True: 'Отличная погода для путешествий',
            False: 'Сегодня не лучшая погода для путешествий',
        }

        start_weather_evaluation, start_weather_reasons = check_bad_weather(weather_info_start)
        end_weather_evaluation, end_weather_reasons = check_bad_weather(weather_info_end)

        rus = {
            'temperature': 'Температура, C',
            'humidity': 'Влажность, %',
            'wind_speed': 'Скорость ветра, m/s',
            'precipitation_probability': 'Вероятность осадков, %'
        }

        start_reasons_formatted = ''
        end_reasons_formatted = ''

        if len(start_weather_reasons) > 0:
            start_reasons_formatted = ('Негативные факторы: ' +
                                       ', '.join(map(lambda x: rus[x], start_weather_reasons)))
        if len(end_weather_reasons) > 0:
            end_reasons_formatted = ('Негативные факторы: ' +
                                     ', '.join(map(lambda x: rus[x], end_weather_reasons)))


        return render_template("result.html", start_city=start, end_city=end,
                               start_weather=Markup(weather_states[start_weather_evaluation] + '<br/>' +  start_reasons_formatted),
                               end_weather=Markup(weather_states[end_weather_evaluation] + '<br/>' + end_reasons_formatted))
    else:
        return "Ошибка при получении данных о погоде.", 400


if __name__ == '__main__':
    app.run(debug=True)