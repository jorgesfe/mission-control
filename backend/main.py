import sys
import psutil
import gpustat
from flask import Flask, request, jsonify, make_response, render_template, session, flash
import jwt
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = 'KEEP_IT_A_SECRET'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],  algorithms=['HS256'])
        except:
            return jsonify({'message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form['username'] and request.form['password'] == '123456':
        token = jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(minutes=50))
        }, app.config['SECRET_KEY'],  algorithms=['HS256'])
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed"'})


@app.route("/info")
@token_required
def getComputerInfo():
    op_system = sys.platform;
    cpu_usage = psutil.cpu_percent(interval=1)
    temperature = None
    if op_system.__contains__("linux"):
        temperature = psutil.sensors_temperature()
    memory_usage = psutil.virtual_memory()[2]
    gpu_stats = gpustat.GPUStatCollection.new_query()
    return {
        "cpuUsage": cpu_usage,
        "memoryUsage": memory_usage,
        "temperature": temperature
    }

#@app.route("/script", methods=['GET'])
#@token_required
#def add_script():
#    return

#@app.route("/script", methods=['POST'])
#def add_script():
#    return

#@app.route("/run", methods=['POST'])
#def run_script():
#    return


app.run()
