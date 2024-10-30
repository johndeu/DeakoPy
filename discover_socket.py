# discover devices on the network via sockets
# Does not work on my mac, so stick with the mdns version
import asyncio
from pydeako import deako, discover

async def _discover():
    client_name = "MyClient"
    d = discover.DeakoDiscoverer()
    deako_client = deako.Deako(d.get_address, client_name=client_name)

    await deako_client.connect()
    await deako_client.find_devices()

    devices = deako_client.get_devices()

    # turn on all devices
    for uuid in devices:
        await deako_client.control_device(uuid, True)

if __name__ == "__main__":
    asyncio.run(_discover())