import time
import sys
import argparse
import json

from VersionAlejo.entidades.sensor_publisher import Sensor


# Verify arguments
def verify_args():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Sensor - Introduction to Distributed Systems")

    # Define the arguments
    required_named = parser.add_argument_group('required arguments')
    # Al crear un argumento, y ponerle un nombre largo, automáticamente queda vinculado
    required_named.add_argument('-c', '--config', help='JSON configuration file', required=True)
    required_named.add_argument('-t', '--type', choices=['temperature', 'PH', 'oxygen'], help='Sensor type',
                                required=True)
    required_named.add_argument('-i', '--interval', type=int, help='Time interval (in seconds)', required=True)

    # Parse command-line arguments
    args = parser.parse_args()

    return args


# end def

# Create sensor with the obtained arguments
def create_sensor(args):
    try:
        with open(args.config, 'r') as file:
            data = json.load(file)
            # MISSING
            # Verify that 'correct', 'out_of_range', and 'error' are present in the JSON
            # Verify: Sum probabilities = 1
            sensor = Sensor(args.type, args.interval, data)
            return sensor
        # end with

    except FileNotFoundError:
        print(f"The file {args.config} was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"The file {args.config} is not a valid JSON.")
        sys.exit(1)
    # end try


# end def


def main():
    # Verify command-line arguments
    args = verify_args()

    # Create a sensor object based on the arguments
    sensor = create_sensor(args)

    try:
        # Continuous loop to send sensor data
        while True:
            sensor.send()
            time.sleep(sensor.interval)
        # end while
    except KeyboardInterrupt:
        # Close the publisher and terminate the ZeroMQ context on KeyboardInterrupt
        sensor.publisher.close()
        sensor.context.term()
    # end try


# end def


if __name__ == "__main__":
    main()
# end if

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
