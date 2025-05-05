from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/logs', methods=['GET'])
def download_logs():#downloads log from server
    log_path = os.path.join(os.path.dirname(__file__), "crafting_log.txt")

    if not os.path.exists(log_path):
        return "Log file not found", 404

    return send_file(log_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)