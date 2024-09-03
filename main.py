import configparser
import qbittorrent
import time

# Load config
config = configparser.ConfigParser()
config.read("config.ini")
qbittorrent_client = config["DEFAULT"]["QBITTORRENT_CLIENT"]
debug = config["DEFAULT"].getboolean("DEBUG")

# Connect to qbittorrent
qb = qbittorrent.Client(qbittorrent_client)
torrents = qb.torrents()

# Debug info
if debug:
    print(f"[DEBUG]: There are {len(torrents)} torrents")

# List torrents
for torrent in torrents:
    print(torrent["name"])
    time.sleep(2)
