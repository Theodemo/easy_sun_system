#!/usr/bin/env python3
# Auteur : Théo de Morais
# Date : 10 août 2023
import os
import minimalmodbus
import sqlite3
import time
import threading
from flask import Flask, render_template, request, jsonify
from waitress import serve
from serial import SerialException
import subprocess
from datetime import datetime
import socket
import re


PVV = 15205
CHARGW = 15208
BATV=15206
BATSOC=25275
LOADW= 25215
LOADPCENT=25216


DATABASE = 'data.db'


PORT = '/dev/ttyUSB0'
SLAVE_ADDRESS = 4
BAUDRATE = 19200
TIMEOUT = 0.5


SAVE_INTERVAL = 3*60 
CLEAR_INTERVAL= 24 * 60 * 60

instrument=None
pause_event = threading.Event()


app = Flask(__name__)


def init_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value REAL, timestamp INTEGER)''')
    conn.commit()
    conn.close()


def save_register_value(register_name, value):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
              (register_name, value, int(time.time())))
    conn.commit()
    conn.close()


def clear_register_values():
    years_ago_timestamp = int(time.time()) - (365 * 24 * 60 * 60)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM registers WHERE timestamp < ?", (years_ago_timestamp,))
    conn.commit()
    conn.close()

def query_register_value(register_name, start_datetime, end_datetime):
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  


        c = conn.execute("SELECT value, timestamp FROM registers WHERE name = ? AND timestamp BETWEEN ? AND ?",(register_name, start_datetime, end_datetime))

        result = c.fetchall()
        conn.close()

        values = [item['value'] for item in result]
        timestamps = [item['timestamp'] for item in result]

        consommation_totale_value = consommation_totale(values, timestamps)
        consommation_totale_value = round(consommation_totale_value, 2)

        return values, timestamps, consommation_totale_value
    except sqlite3.Error as e:
        return [], [], 0


def consommation_totale(puissance_watts, temps_secs):

    if len(puissance_watts) != len(temps_secs):
        return 0

    if not puissance_watts or not temps_secs:
        return 0

    consommation_joules = 0
    previous_time = temps_secs[0] 


    for puissance, temps in zip(puissance_watts, temps_secs):
        duree = temps - previous_time
        consommation_joules += puissance * duree
        previous_time = temps


    consommation_kwh = consommation_joules / 3600000.0

    return consommation_kwh


#-----------------------------------------------------------------------------#


def initialize_instrument():
    global instrument
    while True:
        try:
            if instrument is not None:
                instrument.serial.close()
                instrument=None
            time.sleep(2)
            instrument = minimalmodbus.Instrument(PORT, SLAVE_ADDRESS)
            instrument.serial.baudrate = BAUDRATE
            instrument.serial.timeout = TIMEOUT
            return
        except Exception as e:
            if instrument is not None:
                instrument.serial.close()
                instrument=None

            time.sleep(60)


def read_register(register):
    time.sleep(1)
    global instrument
    try:
        return instrument.read_registers(register, 1)[0]

    except SerialException as e:
        pause_event.set() 
        initialize_instrument()
        pause_event.clear()
        return None
    except Exception as e:
        pause_event.set()
        initialize_instrument()
        pause_event.clear()
        return None


def read_registers():
    pvv = read_register(PVV)
    if pvv is not None:
        pvv = pvv * 0.1
        pvv = round(pvv, 2)
    chargw = read_register(CHARGW)
    batv = read_register(BATV)
    if batv is not None:
        batv=batv*0.1
        batv = round(batv, 2)
    batsoc = read_register(BATSOC)
    loadw = read_register(LOADW)
    loadpcent = read_register(LOADPCENT)
    return [pvv,chargw,batv,loadw,loadpcent]

def save_registers():
    chargw = read_register(CHARGW)
    loadw = read_register(LOADW)
    if chargw is not None:
        save_register_value('CHARGW', chargw)
    if loadw is not None:
        save_register_value('LOADW', loadw)


#----------------------------------------------------------#

def save_task():
    while True:
        save_registers()
        time.sleep(SAVE_INTERVAL)


def clear_task():
    while True:
        clear_register_values()
        time.sleep(CLEAR_INTERVAL)


#------------------------------------------------------------------#
def configure_wifi(ssid, password):
    wpa_supplicant_content = f"""country=fr
update_config=1
ctrl_interface=/var/run/wpa_supplicant

network={{
    scan_ssid=1
    ssid="{ssid}"
    psk="{password}"
}}"""
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as wpa_file:
        wpa_file.write(wpa_supplicant_content)

def check_wifi_connection(box_name):
    try:
        output = subprocess.check_output(['iwconfig', 'wlan0'])
        output = output.decode('utf-8')
        if box_name in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def get_wlan_ip():
    try:
        output = subprocess.check_output(["ifconfig", "wlan0"]).decode("utf-8")
        ip_pattern = r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        match = re.search(ip_pattern, output)
        
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error getting wlan IP address: {e}")
        return None
#------------------------------------------------------------------#

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3')
def config():
    return render_template('page3.html')
#------------------------------------------------------------------#

@app.route('/update')
def update():
    registers = read_registers()
    return jsonify(registers)

#------------------------------------------------------------------#

@app.route('/chart-data')
def chart_data():
    start_datetime = int(request.args.get('start_datetime'))
    end_datetime = int(request.args.get('end_datetime'))

    values_chargw, timestamps_chargw, total_sum_chargw = query_register_value('CHARGW', start_datetime, end_datetime)
    values_loadw, timestamps_loadw, total_sum_loadw = query_register_value('LOADW', start_datetime, end_datetime)

    chargw = {
        "values": values_chargw,
        "timestamps": timestamps_chargw,
        "total_sum": total_sum_chargw
    }
    loadw = {
        "values": values_loadw,
        "timestamps": timestamps_loadw,
        "total_sum": total_sum_loadw
    }

    data = {"chargw": chargw, "loadw": loadw}
    return jsonify(data)



@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

#------------------------------------------------------------------#


@app.route('/configure', methods=['POST'])
def configure():
    if request.method == 'POST':
        box_name = request.form['box_name']
        password = request.form['password']


        configure_wifi(box_name, password)
    return f"Configuration Wi-Fi appliquée avec succès"

@app.route('/check_connection')
def check_connection():
    box_name = request.args.get('box_name')
    wlan_ip =get_wlan_ip()

    if wlan_ip:
        message = f"La Centrale est connectée. Vous pouvez accéder à la page depuis l'adresse http://{wlan_ip}:5000."
    else:
        message = f"La Centrale n'est pas connectée à la box '{box_name}'."

    return jsonify(message=message)

@app.route('/update_datetime', methods=['POST'])
def update_datetime():
    if request.method == 'POST':
        new_datetime = request.form['new_datetime']

        try:
            new_datetime_obj = datetime.strptime(new_datetime, '%Y-%m-%d %H:%M:%S')

            command = f'sudo date -s "{new_datetime_obj.strftime("%Y-%m-%d %H:%M:%S")}"'
            os.system(command)

            return "L'heure et la date ont été mises à jour avec succès."
        except ValueError as e:
            return f"Erreur lors de la mise à jour de l'heure et de la date : {e}"

@app.route('/clear_data', methods=['POST'])
def clear_data():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("DELETE FROM registers")
            conn.commit()

            c.execute("VACUUM")
            conn.commit()

            conn.close()
            return "Toutes les données ont été effacées avec succès, et la base de données a été optimisée."
        except sqlite3.Error as e:
            return f"Erreur lors de l'effacement des données : {e}"



def start_tasks():
    save_thread = threading.Thread(target=save_task)
    clear_thread = threading.Thread(target=clear_task)
    save_thread.daemon = True
    clear_thread.daemon = True
    save_thread.start()
    clear_thread.start()

def open_ngrok_tunnel(port):
    try:
        ngrok_process = subprocess.Popen(['ngrok', 'http', str(port)])
        # Attendre quelques secondes pour que ngrok soit opérationnel
        time.sleep(5)
        return ngrok_process
    except Exception as e:
        print(f"Erreur lors de l'ouverture du tunnel ngrok : {e}")
        return None

if __name__ == '__main__':

        #initialize_instrument()
        init_database()
        #start_tasks()
        serve(app, host='0.0.0.0', port=5000)
