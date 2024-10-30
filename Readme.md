# Deako Py App

This application is a test project to explore and demonstrate how to interact with Deako Lighting devices using the Deako Lighting SDK. The app discovers Deako devices on the network, allows for basic device control (turning lights on/off, adjusting brightness), and tests toggling functionality with specific devices like the "Coffee bar."

It includes a CLI implementation in the **lights.py** file. 

## Usage

### Running the Deako CLI

Once your environment is set up, you can use the CLI to discover and control Deako devices on your local network.

To run the CLI:

```bash
python lights.py discover
```

### Discovering Devices

The discover command searches for Deako devices on your network and caches the results.

```bash
lights discover
```
### Controlling Devices

You can turn devices on or off by using the on and off subcommands:

```bash
lights on "device_name" --brightness 70
```

```bash
lights off "device_name"
```

### Aliases

You can create aliases for your devices to make controlling them easier.

**Add an alias**:

```bash
lights alias add "shortname" "full_device_name"

lights alias list

lights alias remove "shortname"
```

## Install Deako CLI Script Globally

If you'd like to run the `lights.py` command globally from anywhere on your system using the `lights` command, follow these steps:

### Step 1: Create `lights.sh` Bash Script

In your project folder, create a file called `lights.sh`. This script will automatically activate the virtual environment and run the `lights.py` script.

```bash
#!/bin/bash
# Activate the virtual environment and run the lights.py script
source /path/to/your/project/venv/bin/activate
python /path/to/your/project/lights.py "$@"
```

### Step 2: Make lights.sh Executable

Run the following command to make the lights.sh script executable:
```bash
chmod +x /path/to/your/project/lights.sh
```

### Step 3: Create a Symbolic Link

Now, you’ll want to make the lights.sh script globally accessible. You can do this by creating a symbolic link to a folder that’s in your PATH. Commonly, this would be /usr/local/bin.
```bash
sudo ln -s /path/to/your/project/lights.sh /usr/local/bin/lights
```
This command creates a symbolic link named lights that points to the lights.sh script. You should now be able to run lights from anywhere in your terminal.

### Step 4: Use the Script Globally
Now, you can use the lights command globally to discover or control your Deako devices. For example:
```bash
lights discover
lights on "coffee bar" --brightness 70
lights off "coffee bar"
```
This will execute the lights.py Python script within the virtual environment using the lights command globally.

Make sure your lights.py script is working correctly, and that you have installed all necessary dependencies inside your virtual environment using the steps provided earlier.

You can also check if the virtual environment is being activated properly when running the script globally by echoing environment variables in lights.sh. If needed, adjust your script paths as necessary.

That’s it! You can now control your Deako devices from anywhere in your terminal with a simple command.

## Dev Environment Setup

1. **Install Python 3.11+**:  
   Make sure you have Python 3.11 or newer installed. You can check your Python version by running:

   ```bash
   python --version
   ```

2. **Create a Virtual Environment**:  
   Create a virtual environment in the project directory to manage dependencies:

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:  
   On Linux/macOS, run:

   ```bash
   source venv/bin/activate
   ```

   On Windows, run:

   ```bash
   venv\Scripts\activate
   ```

## Installation

1. **Install Dependencies**:  
   Once the virtual environment is activated, you need to install the `pydeako` library, which is the official Python SDK for Deako devices.

   ```bash
   pip install pydeako
   ```

2. **Clone or Download the Project**:  
   If you haven’t already, clone or download this repository. You can do this by running:

   ```bash
   git clone https://github.com/yourusername/deako-py-app
   ```

   Then navigate into the project directory:

   ```bash
   cd deako-py-app
   ```

## Setup VSCode

If you're using VSCode or another editor, make sure the Python interpreter is set to the virtual environment you created.

1. **Open the Command Palette** in VSCode (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS).
2. Search for **Python: Select Interpreter**.
3. Select the Python interpreter from your virtual environment (`venv`).
   
This ensures that the Python interpreter and dependencies (like `pydeako`) are properly recognized.

---

## Usage

### Running the App

Once your environment is set up, you can run the app to discover and control Deako devices on your local network. The application will discover all the available Deako devices, print their information, and allow you to toggle specific devices like the "Coffee bar" on and off.

To run the app:

```bash
python app.py
```

### What the App Does

1. **Device Discovery**:  
   The app will use mDNS to automatically discover Deako devices on your local network. It retrieves the device names, IP addresses, and other relevant information.

   > **Note**: Discovery only needs to happen **once**. After devices are discovered, the list of devices can be used for subsequent control without rediscovery.

2. **Device Management**:  
   The app stores the discovered devices in a global dictionary, allowing you to reference them by name. Once devices are discovered, you can use their names to send control commands (e.g., toggling the lights on and off) without needing to rediscover the devices.

3. **Controlling Devices**:  
   The app sends control requests to Deako devices. For example, it can turn lights on or off and adjust their brightness levels. The app demonstrates toggling the "Coffee bar" device on and off multiple times to test its functionality.

### Example Output

When you run the app, it will output something like this:

```plaintext
Starting device discovery...
Discovered Device - Name: Coffee bar, IP: 192.168.1.12:23
Device list request sent.

--- Toggle 1: Turning Coffee bar ON ---
Controlling Device: Coffee bar (UUID: d47d1037-3a42-42e0-9a7c-c701cd14f6da)
 - Power: On
 - Brightness: 70%

--- Toggle 1: Turning Coffee bar OFF ---
Controlling Device: Coffee bar (UUID: d47d1037-3a42-42e0-9a7c-c701cd14f6da)
 - Power: Off
 - Brightness: 0%
...
```

### Sample JSON Results

Here are some sample JSON results that the app receives from the Deako devices during discovery and control operations. These examples have been anonymized:

```json
{'type': 'DEVICE_FOUND', 'src': 'deako', 'timestamp': 1730257703, 'data': {'name': 'Living Room', 'uuid': '9c515ea6-10c4-4c6e-b121-e4371e2df36e', 'capabilities': 'power+dim', 'state': {'power': False, 'dim': 35}}}
Found device: Living Room (UUID: 9c515ea6-10c4-4c6e-b121-e4371e2df36e)

Received data: {'type': 'DEVICE_FOUND', 'src': 'deako', 'timestamp': 1730257703, 'data': {'name': 'Office Light', 'uuid': 'd47d1037-3a42-42e0-9a7c-c701cd14f6da', 'capabilities': 'power+dim', 'state': {'power': True, 'dim': 9}}}
Found device: Office Light (UUID: d47d1037-3a42-42e0-9a7c-c701cd14f6da)

Received data: {'type': 'CONTROL', 'transactionId': '6ff45bb2-b3f7-4359-b6f7-551140392100', 'dst': 'client_name', 'src': 'deako', 'status': 'ok', 'timestamp': 1730257706}
```

These responses show how the devices provide information about their state (whether they are powered on, their brightness level, etc.), and how the control commands are acknowledged by the Deako system.

### Customizing Device Control

If you want to customize the behavior (e.g., controlling a different device or adjusting how the brightness is toggled), you can modify the `control_device` function in `app.py`. You can pass in any valid Deako device name and adjust its power state or brightness.

### Known Issues

- Ensure that the device discovery process works by ensuring your Deako devices are connected to the same network as your development environment.
- If the app doesn't find any devices, it may be due to network issues or blocked mDNS traffic. You can try restarting the network connection or checking your firewall settings.

---

## Additional Information

### How It Works

- **Deako SDK**: The app leverages the `pydeako` SDK to discover, connect to, and control Deako Lighting devices. The SDK handles mDNS-based device discovery and communication with the devices using TCP/IP.
- **Asynchronous Execution**: The app uses Python's `asyncio` library to manage asynchronous tasks like device discovery and control, which prevents the app from blocking while waiting for device responses.

### Future Enhancements

This app is designed to demonstrate the basic usage of the Deako SDK, but you can extend it to:
- **Add more complex device control** such as scene management or schedule-based automation.
- **Implement advanced error handling** for network issues or device unresponsiveness.
- **Monitor device state changes** in real-time using continuous updates from Deako devices.

---