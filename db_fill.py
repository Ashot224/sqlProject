import requests
import random

# URL приложения FastAPI
API_BASE_URL = "http://localhost:8002"

def fetch_word_list():
    # Получить список случайных слов
    word_list_url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
    try:
        response = requests.get(word_list_url)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching word list: {e}")
        return ["default", "example", "placeholder", "fallback"]

def generate_actor_data(words_list):
    #Генерация рандомизированных данных актора
    role_types = ["Lead", "Supporting", "Extra", "Villain", "Comedian"]
    genders = ["Male", "Female"]

    return {
        "name": f"{random.choice(words_list).capitalize()} {random.choice(words_list).capitalize()}",
        "role_type": random.choice(role_types),
        "age": random.randint(18, 80),
        "gender": random.choice(genders),
        "rank": f"Rank-{random.randint(1, 10)}"
    }

def send_post_request(endpoint, payload):
 #Отправьте POST-запрос на сервер FastAPI
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload)
        response.raise_for_status()
        print(f"Added actor: {payload['name']}")
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Failed to add actor: {error}")
        return None

def populate_actors_table(words_list, count=100):
    #Заполните таблицу актеров рандомными данными
    for _ in range(count):
        actor_data = generate_actor_data(words_list)
        send_post_request("/actors/", actor_data)

if __name__ == "__main__":
    words = fetch_word_list()
    populate_actors_table(words, count=150)
