from flask import render_template
from app import create_app

config_name = 'development'
app = create_app(config_name)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=8055, debug=True)