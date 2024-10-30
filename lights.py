#!/usr/bin/env python3

import asyncio
import logging
import json
import argparse
import click
import os
from pydeako.discover import DeakoDiscoverer, DevicesNotFoundException
from pydeako.models import state_change_request, device_list_request
from pydeako.deako._manager import _Manager
from pydeako.deako._request import _Request

logging.basicConfig(level=logging.DEBUG)

CACHE_FILE = "devices_cache.json"
ALIASES_FILE = "aliases.json"

# Global dictionary to store discovered devices and controller info
devices_managed = {}

# Load devices from cache
def load_devices():
    if os.path.exists(CACHE_FILE):
        # Load the cached data and ensure proper structure
        data = json.load(open(CACHE_FILE, 'r'))
        if 'controller_ip' in data and 'controller_port' in data and 'devices' in data:
            return data
    return {}

# Save devices and controller IP to cache
def save_devices(controller_ip, controller_port, devices):
    # Ensure each device has a 'name' field before saving
    devices_data = [{'name': name.lower(), **info} for name, info in devices.items()]
    data = {
        'controller_ip': controller_ip,
        'controller_port': controller_port,
        'devices': devices_data
    }
    with open(CACHE_FILE, 'w') as file:
        json.dump(data, file)

# Class to manage and provide addresses of discovered devices and controller
class DeviceAddressProvider:
    def __init__(self, controller_ip, controller_port, devices):
        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.devices = devices.copy()

    async def get_address(self):
        """Return controller IP and port, followed by device IP and names."""
        if self.devices:
            # Return the controller address on the first request
            device = self.devices.pop(0)
            return f"{self.controller_ip}:{self.controller_port}", device['name']
        raise DevicesNotFoundException()

# Discover devices on the network
async def discover_devices(timeout=10):
    discoverer = DeakoDiscoverer()
    devices = []
    try:
        while True:
            try:
                address, name = await discoverer.get_address()
                if address not in [d['ip_port'] for d in devices]:
                    devices.append({'ip_port': address, 'name': name})
                    print(f"Discovered Device - Name: {name}, IP: {address}")
            except DevicesNotFoundException:
                break
    finally:
        discoverer.stop()
    return devices


# Load aliases from the alias cache file
def load_aliases():
    if os.path.exists(ALIASES_FILE):
        return json.load(open(ALIASES_FILE, 'r'))
    return {}

# Save aliases to the alias cache file
def save_aliases(aliases):
    with open(ALIASES_FILE, 'w') as file:
        json.dump(aliases, file)

# Add a new alias to the aliases cache
def add_alias(alias_name, device_name):
    aliases = load_aliases()
    aliases[alias_name.lower()] = device_name.lower()
    save_aliases(aliases)
    print(f"Alias '{alias_name}' for '{device_name}' added successfully.")

# Remove an alias from the aliases cache
def remove_alias(alias_name):
    aliases = load_aliases()
    if alias_name.lower() in aliases:
        del aliases[alias_name.lower()]
        save_aliases(aliases)
        print(f"Alias '{alias_name}' removed successfully.")
    else:
        print(f"Alias '{alias_name}' not found.")

# Resolve a device name through its alias
def resolve_alias(device_name):
    aliases = load_aliases()
    return aliases.get(device_name.lower(), device_name)

# Callback function for incoming JSON data
def incoming_json_callback(incoming_json):
    global devices_managed
    if incoming_json.get("type") == "DEVICE_FOUND":
        device_data = incoming_json.get("data", {})
        name = device_data.get("name")
        uuid = device_data.get("uuid")
        devices_managed[name] = {
            "uuid": uuid,
            "state": device_data.get("state", {}),
            "capabilities": device_data.get("capabilities", "")
        }
        print(f"Found device: {name} (UUID: {uuid})")

# Control the device (turn on/off, set brightness)
async def control_device(manager, name, power=True, brightness=70):
    if name not in devices_managed:
        print(f"Device '{name}' not found.")
        return

    device = devices_managed[name]
    uuid = device['uuid']
    print(f"Controlling Device: {name} (UUID: {uuid})")

    state_change_body = state_change_request(device_uuid=uuid, power=power, dim=brightness, source="client_name")
    request = _Request(body=state_change_body)

    await manager.send_request(request)

    devices_managed[name]["state"]["power"] = power
    if "dim" in devices_managed[name]["state"]:
        devices_managed[name]["state"]["dim"] = brightness

    state = devices_managed[name]["state"]
    print(f" - Power: {'On' if state.get('power') else 'Off'}")
    print(f" - Brightness: {state.get('dim', 'N/A')}%")


# Main function for discovering devices and controlling them
async def main(command, device_name=None, brightness=None):
    global devices_managed

    if command == "discover":
        print("Starting device discovery...")
        devices = await discover_devices(timeout=10)
        if not devices:
            print("No Deako devices found on the network.")
            return

        # Save the discovered controller IP and port to the cache
        controller_ip = devices[0]['ip_port'].split(":")[0]  # First device IP
        controller_port = int(devices[0]['ip_port'].split(":")[1])  # First device port

        # Request the device list from the controller
        devices_managed.clear()
        device_list_body = device_list_request(source="client_name")
        list_request = _Request(body=device_list_body)

        address_provider = DeviceAddressProvider(controller_ip, controller_port, [{'name': 'Controller'}])
        deako_manager = _Manager(
            get_address=address_provider.get_address,
            incoming_json_callback=incoming_json_callback,
            client_name="your_client_name"
        )
        
        await deako_manager.init_connection()
        await deako_manager.send_request(list_request)

        await asyncio.sleep(3)

        if not devices_managed:
            print("No Deako devices found on the network.")
            return

        print(f"Total Devices Found: {len(devices_managed)}")
        for name, device in devices_managed.items():
            print(f"Name: {name} (UUID: {device['uuid']})")

        # Save devices and controller details to cache
        save_devices(controller_ip, controller_port, devices_managed)
        print("Devices cached successfully.")

    else:
        # Load cached devices and controller IP/port
        cached_data = load_devices()
        if not cached_data:
            print("No cached devices found. Please run the discover command.")
            return

        controller_ip = cached_data.get('controller_ip')
        controller_port = cached_data.get('controller_port')
        devices_managed = {device['name']: device for device in cached_data.get('devices', [])}

        if device_name:
            # Resolve device name from aliases
            device_name = resolve_alias(device_name.lower())

        if device_name not in devices_managed:
            print(f"Device '{device_name}' not found.")
            return

        # Create the manager using the controller IP from cache
        address_provider = DeviceAddressProvider(controller_ip, controller_port, list(devices_managed.values()))
        deako_manager = _Manager(
            get_address=address_provider.get_address,
            incoming_json_callback=incoming_json_callback,
            client_name="Home Python Deako Client"
        )

        await deako_manager.init_connection()

        if command == 'off':
            await control_device(deako_manager, device_name, power=False)
        elif command == 'on':
            await control_device(deako_manager, device_name, power=True, brightness=brightness)
        else:
            print("Invalid action. Use 'on' or 'off'.")

        deako_manager.close()
        print("Disconnected from all devices.")


# Click subcommands for the CLI
@click.group(help="Control and manage Deako smart devices via the command line.")
def cli():
    pass

@cli.command(help="Discover Deako devices and cache them.")
def discover():
    """Discover available Deako devices on the network and cache their details."""
    asyncio.run(main("discover"))

@cli.command(help="Turn on a device and optionally set the brightness.")
@click.argument("device_name", required=True)
@click.option("-b", "--brightness", default=70, help="Set brightness level (only for 'on').", show_default=True)
def on(device_name, brightness):
    """Turn ON the specified DEVICE_NAME with an optional BRIGHTNESS level."""
    asyncio.run(main("on", device_name, brightness))

@cli.command(help="Turn off a device.")
@click.argument("device_name", required=True)
def off(device_name):
    """Turn OFF the specified DEVICE_NAME."""
    asyncio.run(main("off", device_name))
@cli.command(help="Add or remove aliases for device names.")
@click.argument("action", type=click.Choice(["add", "remove"]))
@click.argument("alias_name", required=True)
@click.argument("device_name", required=False)  # Only required for 'add'
def alias(action, alias_name, device_name):
    """Add or remove an alias for a DEVICE_NAME."""
    if action == "add":
        if not device_name:
            print("Error: 'device_name' is required when adding an alias.")
            return
        add_alias(alias_name, device_name)
    elif action == "remove":
        remove_alias(alias_name)

if __name__ == "__main__":
    cli()