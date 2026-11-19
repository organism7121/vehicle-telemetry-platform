import asyncio
import argparse
import subprocess
import can
import cantools
import pandas as pd
from ingestor import Ingestor
import repo

async def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "-v",
    #     "--virtual",
    #     action="store_true",
    #     help="Ingest CAN data from SocketCAN as opposed to a physical CAN hardware",
    # )
    parser.add_argument(
        "dbc",
        help="DBC file to decode CAN frames",
    )
    parser.add_argument(
        "log",
        help="Log file to add to database for simulated live monitoring and diagnostics"
    )
    args = parser.parse_args()

    db = cantools.database.load_file(args.dbc)
    log = args.log

    # configure based off -v flag once physical can hardware can be tested
    interface = "socketcan"
    channel = "vcan0"

    ingestor = Ingestor(db)

    repo.create_table()

    with can.Bus(channel=channel, interface=interface) as bus:
        with can.Notifier(bus, [ingestor]):
            subprocess.call(f"python -m can.player -i {interface} -c {channel} {log}", shell=True)

if __name__ == "__main__":
    asyncio.run(main())

