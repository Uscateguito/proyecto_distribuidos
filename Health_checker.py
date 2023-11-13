import zmq

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

IP_ADDRESS = "127.0.0.1"
PORT = "8888"


# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Quality System
class Health_Checker:
    # Method: Constructor
    def __init__(self):
        # Initialize ZeroMQ context and subscriber socket
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.bind(f"tcp://{IP_ADDRESS}:{PORT}")
        # Recibe todoo tipo de mensajes
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")
        print("Quality system running...")

    # end def

    # Method: Receive
    def receive(self):
        # While the program is running, receive messages
        while True:
            message = self.subscriber.recv_multipart()
            print(message)
        # end while
    # end def


# end class

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Información que debo obtener:
# tipo de sensor que se dañó, intervalo en el que ese sensor estaba enviando info
# documento al que estaba vinculado
def main():
    # Create a quality system object and receive messages
    health_checker = Health_Checker()
    try:
        health_checker.receive()
    except KeyboardInterrupt:
        # Close the publisher and terminate the ZeroMQ context on KeyboardInterrupt
        health_checker.subscriber.close()
        health_checker.context.term()
    # end try


if __name__ == "__main__":
    main()
