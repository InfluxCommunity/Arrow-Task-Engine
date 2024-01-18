from flask import Flask, render_template, jsonify, request
from machine_generator import machine, runMachine
import threading
import os

app = Flask(__name__)

machines = {
    'machine1': machine(),
    'machine2': machine(),
    'machine3': machine(),
}

for machine_id, machine in machines.items():
    threading.Thread(target=runMachine, args=[machine], daemon=True).start()

@app.route('/toggle_machine', methods=['POST'])
def toggle_machine():
    machine_id = request.json.get('id', None)
    machine_state = request.json.get('state', None)

    machine = machines.get(machine_id)
    if machine is not None:
        if machine_state == "on":
            print(f"{machine_id} activated")
            machine.toggle_fault()
            print(f"{machine_id} fault activated")
        elif machine_state == "off":
            machine.toggle_fault_off()
            print(f"{machine_id} fault deactivated")

    return jsonify({"status": "success"}), 200


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    MACHINE = os.getenv('MACHINES', 2)
    BROKER = os.getenv('BROKER', "localhost")
    app.run(host='0.0.0.0', port=5005, debug=True)