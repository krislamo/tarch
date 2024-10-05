#!/usr/bin/env python3
"""
Torrent Archiver

Provides functionality for managing datasets distributed through BitTorrent.
It tracks files and reconciles hardlinks between download directories and
archival locations.

"""

import argparse
import os
import sqlite3
import sys

import qbittorrent

# SCHEMA format is YYYYMMDDX
SCHEMA = 202410040

def init_db(conn):
    """
    Initialize database
    """

    c = conn.cursor()
    c.executescript(
        f"""
        PRAGMA user_version = {SCHEMA};
        CREATE TABLE IF NOT EXISTS torrents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info_hash_v1 TEXT NOT NULL UNIQUE,
            info_hash_v2 TEXT UNIQUE,
            name TEXT NOT NULL,
            file_count INTEGER NOT NULL,
            content_path TEXT NOT NULL,
            completed_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            tracker_ids TEXT
        );

        CREATE TABLE IF NOT EXISTS trackers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            torrent_id INTEGER NOT NULL,
            file_index INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            size INTEGER NOT NULL,
            is_downloaded BOOLEAN NOT NULL DEFAULT 0,
            last_checked DATETIME,
            FOREIGN KEY (torrent_id) REFERENCES torrents(id),
            UNIQUE (torrent_id, file_index)
        );

    """
    )
    c.close()


def list_tables(conn):
    """
    List all tables in database
    """
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = c.fetchall()
    c.close()
    return [table[0] for table in table_list]


parser = argparse.ArgumentParser(description="Manage BitTorrent datasets", prog="tarch")
subparsers = parser.add_subparsers(
    dest="command", required=True, help="Available commands"
)

scan_parser = subparsers.add_parser("scan", help="Scan command")
scan_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
scan_parser.add_argument("-d", "--directory", help="Directory to scan")
scan_parser.add_argument("-t", "--type", help="Scan type")
scan_parser.add_argument("-e", "--endpoint", help="Endpoint URL")
scan_parser.add_argument("-u", "--username", help="Username")
scan_parser.add_argument("-p", "--password", help="Password")
scan_parser.add_argument("-s", "--storage", help="Path of sqlite3 database")

args = parser.parse_args()

if args.command == "scan":
    if args.storage is None:
        STORAGE = os.path.expanduser("~/.tarch.db")
    else:
        STORAGE = args.storage
    try:
        sqlitedb = sqlite3.connect(STORAGE)
        tables = list_tables(sqlitedb)
    except sqlite3.DatabaseError as e:
        print(f"[ERROR]: Database \"{STORAGE}\" Error: {str(e)}")
        sys.exit(1)
    if len(tables) == 0:
        print(f"[INFO]: Initializing database at {STORAGE}")
        init_db(sqlitedb)
    cursor = sqlitedb.cursor()
    cursor.execute("PRAGMA user_version;")
    SCHEMA_FOUND = cursor.fetchone()[0]
    cursor.close()
    if not SCHEMA == SCHEMA_FOUND:
        print(f"[ERROR]: SCHEMA {SCHEMA_FOUND}, expected {SCHEMA}")
        sys.exit(1)
    if not args.directory is None:
        print("[INFO]: --directory is not implemented\n")
        sys.exit(0)
    if not args.endpoint is None:
        qb = qbittorrent.Client(args.endpoint)
        torrents = qb.torrents()
        print(f"[INFO]: There are {len(torrents)} torrents\n")
        for torrent in torrents[:10]:
            files = qb.get_torrent_files(torrent["hash"])
            if args.debug:
                print(f"[DEBUG]: {repr(torrent)}")
            print(f"[name]: {torrent['name']}")
            print(f"[infohash_v1]: {torrent['infohash_v1']}")
            print(f"[content_path]: {torrent['content_path']}")
            print(f"[magent_uri]: {torrent['magnet_uri'][0:80]}")
            print(f"[completed_on]: {torrent['completed']}")
            print(f"[file_count]: {len(files)}\n")
