import asyncio
import websockets
import json
from datetime import datetime, timezone
from pathlib import Path
import os
import logging
_log = logging.getLogger(__name__)
root_dir = os.path.abspath(os.path.dirname(__file__))


ais_raw_csv = Path("/data/vessels/aisstream_locs.csv")
logfile_path = Path("/data/log/aisstream.log")

ship_mmsi_ids = {
    "265044200": "Ocean Seeker",
    "265044670": "Ocean Nomad",
    "265035670": "Ocean Rose",
    "265066900": "Ocean Scout",
    "265054270": "Ocean Child",
    "265737840": "Gnarly",
}

bounding_box = [[52, 5], [70, 25]] # [[South, West], [North, East]]


async def connect_ais_stream():
    secrets_file = Path(root_dir) / "ais_secrets.json"
    if not secrets_file.exists():
        _log.error(f"Did not find secrets file {secrets_file}. Create an API key on aisstream.io")
        return
    with open(secrets_file) as json_file:
        secrets = json.load(json_file)

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": secrets["aisstream_api_key"],
                             "BoundingBoxes": [bounding_box],
                             "FiltersShipMMSI": list(ship_mmsi_ids.keys()),
                             "FilterMessageTypes": ["PositionReport"]}

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']
                if str(ais_message['UserID']) in ship_mmsi_ids.keys():
                    vessel_name = ship_mmsi_ids[str(ais_message['UserID'])]
                else:
                    vessel_name = 'unknown'
                with open(ais_raw_csv, "a") as outfile:
                    _log.info(f"logged message from {vessel_name}: {ais_message}")
                    out_str = f"{datetime.now(timezone.utc)},{ais_message['UserID']},{vessel_name},{ais_message['Latitude']},{ais_message['Longitude']}\n"
                    outfile.write(out_str)

if __name__ == "__main__":
    logging.basicConfig(
        filename=logfile_path,
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if not ais_raw_csv.exists():
        _log.info(f"Creating locations file {ais_raw_csv}")
        with open(ais_raw_csv, "w") as outfile:
            outfile.write("datetime,MSSI,vessel_name,latitude,longitude\n")
    _log.info("Start websocket to listen for locations")
    asyncio.run(asyncio.run(connect_ais_stream()))
