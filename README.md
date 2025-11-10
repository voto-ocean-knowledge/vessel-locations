# vessel-locations
Fetch and store locations of vessels

Some assembly required!

### setup

1. Get an API key from https://aisstream.io/ and put it in a file called `ais_secrets.json`
```json
{
  "aisstream_api_key": "your-api-key-here"
}
```
2. Edit the variables **ship_mssi_ids** and **bounding_box** in `fetch_ais_data.py` to the vessels and area you want to monitor.
3. Update the paths of the output **ais_raw_csv** and the logfile **logfile_path**
3. Install websockets `pip install websockets`
4. Run the script with `python fetch_ais_data.py`
5. Tail the csv file you set to see the locations come in over AIS. This can take a few minutes!

In my experience, the websocket that this runs on closes after a few hours (ymmv). I set up a systemd service to restart the process when it dies. You'll need to edit the paths in `ais.service` and set it up with `sudo cp ais.service /etc/systemd/system/ais.service` followed by `sudo systemctl enable ais`.