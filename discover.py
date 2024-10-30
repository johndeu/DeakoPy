from zeroconf import ServiceBrowser, Zeroconf
import socket
import time

class DeakoListener:
    def __init__(self):
        self.devices = []

    def remove_service(self, zeroconf, type, name):
        pass  # Optional: Handle service removal if needed

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            port = info.port
            device_id = name.split('.')[0]
            self.devices.append({'ip': ip, 'port': port, 'name': device_id})

def discover_deako_devices(timeout=5):
    zeroconf = Zeroconf()
    listener = DeakoListener()
    browser = ServiceBrowser(zeroconf, "_deako._tcp.local.", listener)
    
    print("Discovering Deako devices...")
    time.sleep(timeout)  # Wait for discovery
    zeroconf.close()
    return listener.devices

if __name__ == "__main__":
    devices = discover_deako_devices()
    if not devices:
        print("No Deako devices found on the network.")
    else:
        print(f"Found {len(devices)} device(s):")
        for idx, device in enumerate(devices, start=1):
            print(f"{idx}. Name: {device['name']} - IP: {device['ip']} - Port: {device['port']}")