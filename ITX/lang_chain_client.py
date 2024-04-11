import requests

if __name__ == '__main__':
    response = requests.post(
        "http://localhost:9999/city/his/invoke",
        json={'input': {'city': '北京'}}
    )
    print(response.json())