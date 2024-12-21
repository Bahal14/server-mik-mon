# server.py
from flask import Flask, jsonify, request
from librouteros import connect
from librouteros.exceptions import TrapError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Fungsi untuk terhubung dengan Mikrotik
def connect_to_mikrotik():
    host = '192.168.56.2'  # IP Mikrotik
    username = 'admin'
    password = '123456'

    try:
        api = connect(username=username, password=password, host=host)
        return api
    except TrapError as e:
        print(f"Error connecting to Mikrotik: {e}")
        return None

# Endpoint untuk mengambil data IP DNS
@app.route('/api/dns', methods=['GET'])
def get_dns_settings():
    api = connect_to_mikrotik()
    if api is None:
        return jsonify({"error": "Could not connect to Mikrotik"}), 500

    try:
        dns_settings = list(api('/ip/dns/print'))  # Ambil konfigurasi DNS
        print("DNS Settings:", dns_settings)  # Debug respons di server
        return jsonify(dns_settings), 200
    except Exception as e:
        print(f"Error fetching DNS settings: {e}")  # Debugging error
        return jsonify({"error": str(e)}), 500
    finally:
        if api:
            api.close()

@app.route('/api/dns/add', methods=['POST'])
def add_dns_server():
    api = connect_to_mikrotik()
    if api is None:
        print("Failed to connect to Mikrotik")
        return jsonify({"error": "Could not connect to Mikrotik"}), 500

    try:
        data = request.json
        new_dns = data.get('server')
        
        # Validasi DNS baru
        import re
        if not new_dns or not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', new_dns):
            return jsonify({"error": "Invalid DNS format"}), 400

        # Ambil DNS saat ini
        dns_settings = list(api('/ip/dns/print'))
        current_dns = dns_settings[0].get('servers', '') if dns_settings else ''
        updated_dns = f"{current_dns},{new_dns}" if current_dns else new_dns

        # Update DNS di Mikrotik
        response = list(api(cmd='/ip/dns/set', servers=updated_dns))  # Evaluasi respons
        print("Evaluated response from Mikrotik after DNS set:", response)

        # Validasi perubahan DNS
        dns_settings_after = list(api('/ip/dns/print'))
        updated_servers = dns_settings_after[0].get('servers', '')
        if new_dns in updated_servers.split(','):
            return jsonify({"message": f"DNS server '{new_dns}' added successfully", "updated_dns": updated_servers}), 200
        else:
            raise Exception("Failed to update DNS on Mikrotik")

    except Exception as e:
        print(f"Error adding DNS server: {e}")  # Debug error
        return jsonify({"error": f"Server exception: {str(e)}"}), 500
    finally:
        if api:
            api.close()

if __name__ == '__main__':
    app.run(debug=True)
