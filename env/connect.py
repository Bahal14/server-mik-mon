from librouteros import connect
from librouteros.exceptions import TrapError

try:
    api = connect(username='admin', password='123456', host='192.168.56.2')
    for resource in api('/ip/dns/print'):  # Perbaikan perintah untuk mencetak konfigurasi DNS
        print(resource)
except TrapError as e:
    print(f"Error connecting to Mikrotik: {e}")
