import asyncio
import argparse
import subprocess
import can
import cantools
import pandas as pd

# log files
yaris_log = "logs/accellog.log"
yaris_csv = "logs/revlog.csv"
yaris_trc = "logs/noeculog.trc"
tesla_mf4 = "logs/00000001.MF4"

# can bus data storage
rows = []
unknown_ids = {}
# {
#   frame_id: count
# }
decode_errors = [] # (timestamp, frame_id, error_message)

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
    "-l",
    "--log",
    help="Optional log file to add to database for simulated live monitoring and diagnostics"
)
args = parser.parse_args()
db = cantools.database.load_file(args.dbc)

# configure based off -v flag once physical can hardware can be tested
interface = "socketcan"
channel = "vcan0"

def ingest(frame):
    timestamp = frame.timestamp
    frame_id = frame.arbitration_id
    data = frame.data
    try:
        message = db.get_message_by_frame_id(frame_id)
    except KeyError:
        unknown_ids[frame_id] = unknown_ids.get(frame_id, 0) + 1
        return

    try:
        decoded = message.decode(data, decode_choices=False)
    except Exception as e:
        decode_errors.append((timestamp, frame_id, str(e)))
        return

    for signal_name, value in decoded.items():
        rows.append(
            {
                "timestamp": timestamp,
                "frame_id": frame_id,
                "message": message.name,
                "signal": signal_name,
                "value": value,
            }
        )

async def main():
    with can.Bus(channel=channel, interface=interface) as bus:
        with can.Notifier(bus, [ingest]):
            subprocess.call(f"python -m can.player -i {interface} -c {channel} {yaris_log}", shell=True)
            df = pd.DataFrame(rows)
            print("unknown IDs:", {hex(k): v for k, v in sorted(unknown_ids.items())})
            print("decode errors:", decode_errors[:10]) 
            print(df.message)

if __name__ == "__main__":
    asyncio.run(main())

