import zmq
import time
import datetime
import random
import sys
import argparse
import json

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

IP_ADDRESS = "127.0.0.1"
PORT = "6666"

PROBABILITY = {
    'correct': 0.6,
    'out_of_range': 0.3,
    'error': 0.1
}


# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Sensor
class Sensor:

    # Method: Constructor
    def __init__(self, topic, interval, config):
        # Initialize sensor properties
        self.topic = topic
        self.interval = interval
        self.config = config
        # Initialize ZeroMQ context and publisher socket
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(f"tcp://{IP_ADDRESS}:{PORT}")

        # Print a message indicating the sensor is running
        print(self.topic + " sensor running...")

    # end def

    # Method: Generate random value
    def generate_random_value(self):
        # List of possible outcomes
        num = [1, 2, 3]

        # Randomly choose an outcome based on probabilities
        x = random.choices(num, weights=(PROBABILITY['correct'],
                                         PROBABILITY['out_of_range'],
                                         PROBABILITY['error']))[0]

        # Generate and return a value based on the chosen outcome
        if x == 1:
            return str(random.uniform(self.config['lower_bound'], self.config['upper_bound']))
        elif x == 2:
            return str(random.uniform(0, self.config['lower_bound'])
                       if random.random() < 0.5
                       else random.uniform(self.config['upper_bound'], self.config['upper_bound']
                                           + self.config['upper_bound'] / 2))
        elif x == 3:
            return str(-1)
        # end if

    # end def

    # Method: Send new message
    def send(self):
        try:
            # Generate a random value and current time
            value = self.generate_random_value()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Send the data as a multipart message
            self.publisher.send_multipart([self.topic.encode("UTF-8"),
                                           value.encode("UTF-8"),
                                           current_time.encode("UTF-8"),
                                           str(self.interval).encode()])
            # Print the current time and a message indicating the data was sent
            print(current_time)
            print("Message sent:", value)
        except Exception as e:
            print("An error occurred:", str(e))
        # end try
    # end def

# end Sensor

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
