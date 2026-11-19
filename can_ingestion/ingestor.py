import can
import repo

thresh = 100

class Ingestor(can.Listener):
    def __init__(self, db):
        self.db = db
        self.rows = []
        # do something with these later..
        self.unknown_ids = []
        self.decode_errors = []

    def __check_thresh(self):
        # possible loss of last frames
        if len(self.rows) > thresh:
            print(f"threshold reached: {len(self.rows)}>{thresh}")
            print(f"inserting batch")
            repo.insert_batch(self.rows)
            self.rows = []
            print(len(self.rows), '\n')

    def ingest(self, frame):
        timestamp = frame.timestamp
        frame_id = frame.arbitration_id
        data = frame.data
        try:
            message = self.db.get_message_by_frame_id(frame_id)
        except KeyError:
            # these most likely will have to be tuples if inserted into database
            self.unknown_ids.append({
                "timestamp": timestamp,
                "frame_id": frame_id
            })
            return

        try:
            decoded = message.decode(data, decode_choices=False)
        except Exception as e:
            # ^
            self.decode_errors.append({
                "timestamp": timestamp,
                "frame_id": frame_id,
                "message": message.name,
                "decode_err": str(e)
            })
            return

        for signal_name, value in decoded.items():
            self.rows.append((
                timestamp,
                frame_id,
                message.name,
                signal_name,
                value
            ))
        self.__check_thresh()


    def on_message_received(self, frame):
        self.ingest(frame)

    def stop(self):
        ...