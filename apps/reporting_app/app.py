from flask import Flask

# Инициализация Flask-приложения
app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
	return 'Hello from Horeca App!'

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
