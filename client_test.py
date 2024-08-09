import time

import cv2
import grpc
import numpy as np
from grpc._channel import _MultiThreadedRendezvous

import video_pb2, video_pb2_grpc


class TestClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:11111')
        self.stub = video_pb2_grpc.HelloStub(self.channel)

    def send_message(self, message):
        print(message)
        if message > 30:
            print("Message is 30, exiting...")
            return
        try:
            msg = video_pb2.Req(message=message)
            resp = self.stub.callPrc(msg)
            self.send_message(message=resp.message)
        except TypeError as e:
            print(f"TypeError: {e}")


class TestVideoClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:11111')
        self.stub = video_pb2_grpc.VideoStreamStub(self.channel)

    def get_video_frames(self):
        # while True:
        frame: _MultiThreadedRendezvous = self.stub.StreamFrames(video_pb2.Empty())
        for i in frame:
            prev = time.time()
            # print(f"Frame: {frame.result()}")
            # print(f"Frame: {frame}")
            img_array = np.frombuffer(i.data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imshow("Frame", img)
            print(f"Client Time taken: {time.time() - prev}")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
            # yield frame


if __name__ == '__main__':
    client = TestVideoClient()
    client.get_video_frames()
    # client = TestClient()
    # client.send_message(message=1)
