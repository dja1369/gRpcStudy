import grpc
from concurrent import futures
import video_pb2, video_pb2_grpc

class HelloServicer(video_pb2_grpc.HelloServicer):
    def callPrc(self, request, context):
        # print(f"Received message: {request.message}, type: {type(request.message)}")

        request.message += 1
        print(f"Modified message: {request.message}, type: {type(request.message)}")
        return video_pb2.Resp(message=request.message + 1)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    video_pb2_grpc.add_HelloServicer_to_server(HelloServicer(), server)
    server.add_insecure_port('[::]:11111')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()