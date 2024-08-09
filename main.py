import time
from concurrent import futures

import cv2
import grpc
import simplejpeg

import video_pb2, video_pb2_grpc


class StreamingServer(video_pb2_grpc.VideoStreamServicer):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

        # self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # self.video.set(cv2.CAP_PROP_FPS, 60)
        self.frame = None
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    def get_frame(self):
        prev = time.time()
        success, frame = self.video.read()
        # print(f"Frame shape: {frame.shape}")
        if not success:
            return None
        # _, self.frame = cv2.imencode(".jpg", frame)
        self.frame = simplejpeg.encode_jpeg(frame, quality=40, colorspace='BGR')
        print(f"Server Time taken: {time.time() - prev}")
        # print(f"Frame shape: {type(self.frame.tobytes())}")
        # _, self.frame = cv2.imencode(".jpg", frame)
        # print(f"type: {type(self.frame)}"
        #       f"shape: {self.frame[:10]}")

    def StreamFrames(self, request, context):
        while True:
            prev = time.time()
            self.get_frame()
            if self.frame is not None:
                # yield video_pb2.Frame(data=self.frame.tobytes())
                yield video_pb2.Frame(data=self.frame)
            # time.sleep(0.015)
            # print(f"Sever Time taken: {time.time() - prev}")

    def serve(self):
        video_pb2_grpc.add_VideoStreamServicer_to_server(self, self.server)
        # SERVICE_NAMES = (
        #     video_pb2.DESCRIPTOR.services_by_name['VideoStream'].full_name,
        #     reflection.SERVICE_NAME,
        # )
        # reflection.enable_server_reflection(SERVICE_NAMES, self.server)

        self.server.add_insecure_port('[::]:11111')
        self.server.start()
        print("gRPC server started")
        self.server.wait_for_termination()
        print("gRPC server stopped")


if __name__ == '__main__':
    server = StreamingServer()
    server.serve()
