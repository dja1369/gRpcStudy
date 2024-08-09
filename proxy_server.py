import asyncio
import cv2
import numpy as np
import websockets
import grpc
import json
import fractions

from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import BYE
from av.frame import Frame

import video_pb2
import video_pb2_grpc


class VideoStreamClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:11111')
        self.stub = video_pb2_grpc.VideoStreamStub(self.channel)

    def get_video_frames(self):
        return self.stub.StreamFrames(video_pb2.Empty())


class VideoToRtcChain(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.grpc_client = VideoStreamClient()
        self.frame = self.grpc_client.get_video_frames()

    async def recv(self):
        frame = next(self.frame)
        img = np.frombuffer(frame.data, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        rtc_frame = video_pb2.Frame.from_ndarray(img, format='bgr24')
        rtc_frame.pts = frame.timestamp
        rtc_frame.time_base = fractions.Fraction(1, 1000)
        return rtc_frame


async def handle_offer(offer, pc):
    pc.addTrack(VideoToRtcChain())

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer['sdp'], type=offer['type']))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return pc.localDescription


async def signaling_handler(websocket):
    pc = RTCPeerConnection()

    async for msg in websocket:
        data = json.loads(msg)
        if data["type"] == "offer":
            answer = await handle_offer(data, pc)
            await websocket.send(json.dumps({"type": "answer", "sdp": answer.sdp}))
        elif data["type"] == "candidate":
            candidate = data["candidate"]
            await pc.addIceCandidate(candidate)
        elif data["type"] == "bye":
            await websocket.send(json.dumps({"type": "bye"}))
            await pc.close()
            break


async def main():
    async with websockets.serve(signaling_handler, "localhost", 3000):
        print("server Run!")
        print("Wait My Signal")
        await asyncio.Future()



if __name__ == '__main__':
    asyncio.run(main())
