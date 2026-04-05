import time
import zmq

context = zmq.Context()
socket_receiver = context.socket(zmq.PULL)
socket_receiver.bind("tcp://*:5555")

socket_broadcast = context.socket(zmq.PUB)
socket_broadcast.bind("tcp://*:5556")

log = []
while True:
    #  Wait for next request from client
    log.append(socket_receiver.recv())

    message = log.pop(0)
    print("Received request: %s" % message.decode('utf-8'))

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket_broadcast.send(message)