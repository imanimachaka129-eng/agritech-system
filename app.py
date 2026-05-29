from flask import Flask, redirect, url_for
from config import Config
from database import init_db

app = Flask(__name__)
app.config.from_object(Config)

init_db()

from routes.auth import auth_bp
from routes.shamba import shamba_bp
from routes.sensor import sensor_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(shamba_bp)
app.register_blueprint(sensor_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)