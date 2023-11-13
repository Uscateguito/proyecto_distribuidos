import argparse
from datetime import datetime

import zmq

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

LIMIT_VALUES = {"temperature": (68, 89), "PH": (6.0, 8.0), "oxygen": (2.0, 11.0)}

IP_ADDRESS_PROXY = "127.0.0.1"
PORT_PROXY = "5555"

IP_ADDRESS_QUALITY_SYSTEM = "127.0.0.1"
PORT_QUALITY_SYSTEM = "7777"

# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Monitor
class Monitor:

    # Method: Constructor
    # Se crea el socket de tipo subscriber, se vincula a un tema
    # al mismo tiempo se crea un socket publisher que enviará información al quality system
    def __init__(self, topic):
        # Initialize ZeroMQ context and subscriber socket
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        # El topic en zeroMQ es un filtro, por lo que solo recibirá los mensajes que tengan ese topic
        self.topic = topic
        # Connect permite vincular un tipo de socket a una dirección
        self.subscriber.connect(f"tcp://{IP_ADDRESS_PROXY}:{PORT_PROXY}")
        # Setsockopt_string permite establecer opciones para el socket
        # en este caso se establece el topic
        # otras opciones válidas son: ZMQ_SUBSCRIBE, ZMQ_UNSUBSCRIBE, ZMQ_IDENTITY, ZMQ_SUBSCRIBE_UNSUBSCRIBE
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
        # Initialize publisher socket
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(
            f"tcp://{IP_ADDRESS_QUALITY_SYSTEM}:{PORT_QUALITY_SYSTEM}"
        )
        print(topic + " monitor running...")

    # end def

    # Method: Receive
    def receive(self):
        # While the program is running, receive messages
        while True:
            message = self.subscriber.recv_multipart()
            received_value = message[1].decode()
            time_stamp = message[2].decode()
            print(time_stamp, ": ", received_value)
            # Check if the received value is within the limits
            self.check_value(received_value, time_stamp)
            # self.performance_test(time_stamp)

        # end while

    # end def

    # Method: Quality control

    # Method: Send alarm
    def send_alarm(self, message):
        # Send the alarm message to the quality system
        try:
            self.publisher.send_string(str(message))
        except Exception as e:
            print("An error occurred:", str(e))
        # end try

    # end def

    # Method: Check value
    def check_value(self, received_value, time_stamp):
        # Check if the received value is within the limits
        if float(received_value) < 0:
            self.send_alarm(
                time_stamp
                + ": "
                + self.topic
                + " was an error with value: "
                + received_value
            )
        elif LIMIT_VALUES[self.topic][0] > float(received_value):
            self.send_alarm(
                time_stamp
                + ": "
                + self.topic
                + " is too low, the current "
                + self.topic
                + " is: "
                + received_value
            )
        elif LIMIT_VALUES[self.topic][1] < float(received_value):
            self.send_alarm(
                time_stamp
                + ": "
                + self.topic
                + " is too high, the current "
                + self.topic
                + " is: "
                + received_value
            )

        # end if
    # end def

    # Method: Performance Test
    def performance_test(self, time_stamp):
        source_message_time = datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        time_delta = current_time - source_message_time
        print(f"The time from occurrence to storage of the measurement is: {time_delta}")

    # end def


# end class