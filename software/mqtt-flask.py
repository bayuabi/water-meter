import pymysql
from flask import Flask , jsonify, render_template
from flask_mqtt import Mqtt
from datetime import datetime

def connection():
    conn = pymysql.connect(host='localhost',
                            user = 'root',
                            passwd = '',
                            db = 'watermeter')
    c = conn.cursor()

    return c, conn


app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '127.0.0.1'
app.config['MQTT_BROKER_PORT'] = 1883

mqtt = Mqtt(app)

volume = None
debit = None

c, conn = connection()
# c.execute("INSERT INTO watermeter(debit, volume) VALUES ({}, {})".format(float(2), float(3)))
# conn.commit()

# c.execute("SELECT * FROM watermeter ORDER BY id DESC LIMIT 1")
# lastId = c.fetchall()[0][0]

lastId = None

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe([("debit", 0), ("volume", 0)])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    now = datetime.now()
    time = now.strftime("%H:%M")

    if message.topic == "volume":
        volume = message.payload.decode()
        c.execute("INSERT INTO VOLUME(TIME, VOLUME) VALUES (%s, %s)", (time, volume))
        conn.commit()
        
    if message.topic == "debit":
        debit = message.payload.decode()
        c.execute("INSERT INTO DEBIT(TIME, DEBIT) VALUES (%s, %s)", (time, debit))
        conn.commit()

    # print('debit: {}'.format(float(debit)))
    # print('volume: {}'.format(float(volume)))
    

@app.route("/")
def homePage():

    return render_template("index.html")

@app.route("/get-data")
def getData():
    debits = []
    volumes = []
    times = []

    c.execute("SELECT * FROM VOLUME ORDER BY NO DESC LIMIT 15")
    volumeTable = c.fetchall()
    for volume in volumeTable:
        volumes.append(float(volume[2]))
        times.append(volume[1])

    c.execute("SELECT * FROM DEBIT ORDER BY NO DESC LIMIT 15")
    debitTable = c.fetchall()
    for debit in debitTable:
        debits.append(float(debit[2]))

    return jsonify(volume=volumes, debit=debits, time=times)

@app.route("/charts")
def charts():

    return render_template("charts.html")

if __name__ == "__main__":
    app.secret_key = ('sadasfjdshf324878hbsdfhbdnf')
    app.run(debug=True)
