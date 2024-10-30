import asyncio
import logging
from pydeako.discover import DeakoDiscoverer, DevicesNotFoundException
from pydeako.models import state_change_request, device_list_request
from pydeako.deako._manager import _Manager
from pydeako.deako._request import _Request

# Set up logging to debug level to print detailed logs for each action.
logging.basicConfig(level=logging.DEBUG)

# Global dictionary to store discovered devices, keyed by device names
devices_managed = {}

# Asynchronous address provider class used to manage and return addresses of discovered devices
class DeviceAddressProvider:
    def __init__(self, devices):
        # Copy the list of discovered devices to avoid modifying the original list.
        self.devices = devices.copy()

    async def get_address(self):
        """Asynchronously provide the next device's address and name."""
        # If there are devices available, return the next device's IP address and name
        if self.devices:
            device = self.devices.pop(0)  # Pop the first device from the list
            ip_port = device['ip_port']
            name = device['name']
            print(f"get_address called, returning (ip_port={ip_port}, name={name})")
            return ip_port, name
        else:
            # If no devices are left, raise an exception that no devices are available
            print("get_address called, no devices left")
            raise DevicesNotFoundException()

# Asynchronous function to discover devices on the network
async def discover_devices(timeout=10):
    # Create an instance of DeakoDiscoverer, which uses mDNS to find Deako devices on the network
    discoverer = DeakoDiscoverer()
    devices = []
    try:
        # Continuously try to discover devices until DevicesNotFoundException is raised
        while True:
            try:
                # Get the address (IP and port) and name of each discovered device
                address, name = await discoverer.get_address()
                ip_port = address
                # Check if the device has already been added, and add it if it’s new
                if not any(d['ip_port'] == ip_port for d in devices):
                    devices.append({'ip_port': ip_port, 'name': name})
                    print(f"Discovered Device - Name: {name}, IP: {ip_port}")
            except DevicesNotFoundException:
                # Stop the discovery if no more devices are found
                break
    finally:
        # Stop the discovery process when done
        discoverer.stop()
    return devices

# Callback function to handle incoming JSON data from the Deako Manager
def incoming_json_callback(incoming_json):
    global devices_managed
    print(f"Received data: {incoming_json}")

    # If the incoming message contains a device found response, process it
    if incoming_json.get("type") == "DEVICE_FOUND":
        # Extract the device data (name, UUID, state, capabilities)
        device_data = incoming_json.get("data", {})
        name = device_data.get("name")
        uuid = device_data.get("uuid")
        # Store the device details in the global dictionary with the device's name as the key
        devices_managed[name] = {
            "uuid": uuid,
            "state": device_data.get("state", {}),
            "capabilities": device_data.get("capabilities", "")
        }
        print(f"Found device: {name} (UUID: {uuid})")

# Function to send a request to change the state of a device (e.g., turn on/off, change brightness)
async def control_device(manager, name, power=True, brightness=70):
    try:
        # Check if the device exists in the devices_managed dictionary
        if name not in devices_managed:
            print(f"Device '{name}' not found.")
            return
        
        # Retrieve the device's UUID and other details
        device = devices_managed[name]
        uuid = device['uuid']

        print(f"\nControlling Device: {name} (UUID: {uuid})")
        
        # Create a state change request to control the device (turn on/off, change brightness)
        state_change_body = state_change_request(device_uuid=uuid, power=power, dim=brightness, source="client_name")
        request = _Request(body=state_change_body)

        # Send the request using the Deako manager
        await manager.send_request(request)
        
        # Update the local device state in the devices_managed dictionary
        devices_managed[name]["state"]["power"] = power
        if "dim" in devices_managed[name]["state"]:
            devices_managed[name]["state"]["dim"] = brightness
        
        # Print the updated state of the device (power and brightness)
        state = devices_managed[name]["state"]
        print(f" - Power: {'On' if state.get('power') else 'Off'}")
        print(f" - Brightness: {state.get('dim', 'N/A')}%")
    except Exception as e:
        # Handle any errors that occur while controlling the device
        print(f"Failed to control device '{name}': {e}")

# Main asynchronous function that orchestrates the entire flow
async def main():
    global devices_managed

    # Step 1: Discover Devices on the network
    print("Starting device discovery...")
    devices = await discover_devices(timeout=10)
    
    if not devices:
        print("No Deako devices found on the network.")
        return
    
    # Print the total number of discovered devices
    print(f"\nTotal Devices Found: {len(devices)}")
    for idx, device in enumerate(devices, start=1):
        print(f"{idx}. Name: {device['name']} - IP: {device['ip_port']}")
    
    # Step 2: Initialize the DeviceAddressProvider with the discovered devices
    address_provider = DeviceAddressProvider(devices)

    # Step 3: Initialize the Deako Manager to manage the connections and commands to the devices
    deako_manager = _Manager(
        get_address=address_provider.get_address,
        incoming_json_callback=incoming_json_callback,  # Set the callback function to process incoming responses
        client_name="your_client_name"  # Set a name for your client
    )

    # Step 4: Establish a connection to the Deako devices
    await deako_manager.init_connection()

    # Step 5: Send a request to the Deako Manager to get a list of devices
    device_list_body = device_list_request(source="client_name")
    list_request = _Request(body=device_list_body)
    await deako_manager.send_request(list_request)
    print("Device list request sent.")

    # Wait briefly to allow time for the devices to respond and be registered
    await asyncio.sleep(3)

    # Step 6: Control the "Coffee bar" device - turn it on and off 3 times
    if "Coffee bar" in devices_managed:
        for i in range(3):
            # Turn the "Coffee bar" on
            print(f"\n--- Toggle {i+1}: Turning Coffee bar ON ---")
            await control_device(deako_manager, "Coffee bar", power=True, brightness=70)
            await asyncio.sleep(2)  # Wait 2 seconds
            
            # Turn the "Coffee bar" off
            print(f"\n--- Toggle {i+1}: Turning Coffee bar OFF ---")
            await control_device(deako_manager, "Coffee bar", power=False, brightness=0)
            await asyncio.sleep(2)  # Wait 2 seconds
    else:
        # If the "Coffee bar" device is not found, print an error message
        print("No 'Coffee bar' device found.")

    # Step 7: Disconnect from the Deako devices and close the connection
    deako_manager.close()
    print("\nDisconnected from all devices.")

# Run the main asynchronous function when the script is executed
if __name__ == "__main__":
    asyncio.run(main())