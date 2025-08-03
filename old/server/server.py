from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import sys
import json
import time
import psutil
import logging
import requests
import socket
from threading import Thread, Lock

log = logging.getLogger('werkzeug')
log.disabled = True

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

CONFIG_FILE = "config.json"
ICON_FILE = "icon.svg"
DATA_DIR = "data"
MAP_FILE = "map.zip"
HEARTBEAT_TIMEOUT = 15

player_heartbeats = {}
lock = Lock()

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"server_name": "Default Server"}, f)

@app.route('/list-files', methods=['GET'])
def list_files():
    folder = request.args.get('folder')
    if not folder:
        return jsonify({"error": "Folder name is required"}), 400

    base_path = os.path.join(os.getcwd(), 'data')

    folder_path = os.path.join(base_path, folder)

    if not os.path.exists(folder_path):
        return jsonify({"error": f"Folder '{folder}' does not exist"}), 404

    try:
        files = os.listdir(folder_path)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config.json', methods=['GET', 'OPTIONS'])
def get_config():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    if os.path.exists(CONFIG_FILE):
        return send_from_directory('.', CONFIG_FILE)
    return "Config not found", 404

@app.route('/map.zip', methods=['GET', 'OPTIONS'])
def get_map():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    if os.path.exists(MAP_FILE):
        return send_from_directory('.', MAP_FILE)
    return "Map not found", 404

@app.route('/icon.svg', methods=['GET', 'OPTIONS'])
def get_icon():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    if os.path.exists(ICON_FILE):
        return send_from_directory('.', ICON_FILE)
    return "Icon not found", 404

@app.route('/heartbeat', methods=['POST', 'OPTIONS'])
def heartbeat():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.json
    player_id = data.get('player_id')
    room_id = data.get('room_id')

    if not player_id or not room_id:
        return "Invalid data", 400

    room_path = os.path.join(DATA_DIR, room_id)
    os.makedirs(room_path, exist_ok=True)  # Ensure room directory exists

    player_file = os.path.join(room_path, f"{player_id}.json")
    if not os.path.exists(player_file):
        with open(player_file, 'w') as f:
            json.dump({"player_id": player_id, "room_id": room_id, "status": "active"}, f)

    # Update heartbeat time
    with lock:
        player_heartbeats[(room_id, player_id)] = time.time()

    return "Heartbeat received", 200

@app.route('/player/get', methods=['GET', 'OPTIONS'])
def get_player():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    player_id = request.args.get('player_id')
    room_id = request.args.get('room_id')

    player_file = os.path.join(DATA_DIR, room_id, f"{player_id}.json")
    if os.path.exists(player_file):
        with open(player_file, 'r') as f:
            player_data = json.load(f)
        response = jsonify(player_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/players/<room_id>', methods=['GET', 'OPTIONS'])
def get_players_in_room(room_id):
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    room_path = os.path.join(DATA_DIR, room_id)
    if not os.path.exists(room_path):
        return "Room not found", 404

    players = []
    for player_file in os.listdir(room_path):
        if player_file.endswith(".json"):
            with open(os.path.join(room_path, player_file), 'r') as f:
                player_data = json.load(f)
                players.append(player_data)
    
    return jsonify(players)

@app.route('/delete_player/<room_id>/<player_id>', methods=['DELETE', 'OPTIONS'])
def delete_player(room_id, player_id):
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    player_file = os.path.join(DATA_DIR, room_id, f"{player_id}.json")
    if os.path.exists(player_file):
        os.remove(player_file)
        return "Player deleted", 200
    return "Player not found", 404

@app.route('/player/create', methods=['POST', 'OPTIONS'])
def create_player():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.json
    player_id = data.get('player_id')
    room_id = data.get('room_id')

    if not player_id or not room_id:
        return "Invalid data", 400

    room_path = os.path.join(DATA_DIR, room_id)
    os.makedirs(room_path, exist_ok=True)  # Ensure room directory exists

    player_file = os.path.join(room_path, f"{player_id}.json")
    if not os.path.exists(player_file):
        with open(player_file, 'w') as f:
            json.dump({"player_id": player_id, "room_id": room_id, "status": "active"}, f)

    return "Player created", 200


@app.route('/player/set', methods=['POST', 'OPTIONS'])
def set_player_data():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.json
    player_id = data.get('player_id')
    room_id = data.get('room_id')
    player_data = data.get('data')

    if not player_id or not room_id or not player_data:
        return "Invalid data", 400

    player_file = os.path.join(DATA_DIR, room_id, f"{player_id}.json")
    if os.path.exists(player_file):
        with open(player_file, 'w') as f:
            json.dump({"player_id": player_id, "room_id": room_id, "data": player_data}, f)
        return "Player data updated", 200

    return "Player not found", 404


@app.route('/room/create', methods=['POST', 'OPTIONS'])
def create_room():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.json
    room_id = data.get('room_id')

    if not room_id:
        return "Invalid data", 400

    room_path = os.path.join(DATA_DIR, room_id)
    if not os.path.exists(room_path):
        os.makedirs(room_path)

    return "Room created", 200

def cleanup():
    while True:
        with lock:
            current_time = time.time()
            for (room_id, player_id), last_heartbeat in list(player_heartbeats.items()):
                if current_time - last_heartbeat > HEARTBEAT_TIMEOUT:
                    player_heartbeats.pop((room_id, player_id), None)
                    player_file = os.path.join(DATA_DIR, room_id, f"{player_id}.json")
                    if os.path.exists(player_file):
                        os.remove(player_file)

            for room_id in os.listdir(DATA_DIR):
                room_path = os.path.join(DATA_DIR, room_id)
                if not os.listdir(room_path):
                    os.rmdir(room_path)

        time.sleep(1)

def run_app():
    Thread(target=cleanup, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)

def print_ip():
    name = server_name()
    internal_ip = get_internal_ip()
    external_ip = requests.get("https://api.ipify.org").text

    print(f"Server Name: {name}")
    print(f"Server running on internal IP {internal_ip}:5000")
    print(f"Server running on external IP {external_ip}:5000 (If Configured)")

def get_internal_ip():
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith('169.254'):
                if addr.address.startswith('192.168.1'):
                    return addr.address

def server_name():
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
            if 'server-info' in config and 'name' in config['server-info']:
                return config['server-info']['name']
            else:
                print("Configuration file invalid.")
                return "[CONFIG INVALID]"
    except FileNotFoundError:
        print(f"Configuration file not found, creating with defaults.")
        return "Default Server"
    except json.JSONDecodeError:
        print("Configuration file invalid.")
        return "[CONFIG INVALID]"

def display_ascii_art():
    art = r"""
 █████    ████  █████   █████     ██████     █████         ███████████     ██████     ███████████    
 ██████   ████  █████   █████   ██████████   █████         ███████████   ██████████   ████████████   
 ███████  ████  █████   █████  ████████████  █████         ███████████  ████████████  █████████████  
 ████████ ████  █████   █████  █████  █████  █████         █████        █████  █████  █████   ████   
 █████████████  █████   █████  █████   ████  █████         █████        █████  █████  █████   ████   
 █████████████  █████   █████  █████         █████         ██████████   ████████████  ████████████   
 █████████████  █████   █████  █████         █████         ██████████   ████████████  █████████████  
 █████████████  █████   █████  █████   ████  █████         █████        █████  █████  █████  ██████  
 █████ ███████  ██████ ██████  █████  █████  █████         █████        █████  █████  █████   █████  
 █████  ██████  █████████████  ████████████  ████████████  ███████████  █████  █████  █████   █████  
 █████   █████    █████████     ██████████   ████████████  ███████████  █████  █████  █████   █████  
 █████    ████      █████         ██████     ████████████  ███████████  ████    ████  █████   █████  
    """
    print(f"\033[1;32m{art}\033[0m")

if __name__ == '__main__':
    display_ascii_art()
    print_ip()

    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    thread_main = Thread(target=run_app)
    thread_main.start()
    thread_main.join()
