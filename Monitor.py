import argparse
import json
import time

from entidades.monitor_subscriber import Monitor

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Global Values

datos_json = {"mensaje": []}


# end Global Values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def validate_arguments():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Sensor Argument Validator")
    # Define the arguments
    parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=["temperature", "PH", "oxygen"],
        help="Monitor type (temperature, ph, or oxygen)",
    )

    args = parser.parse_args()
    return args


# end def


# Method: Main
def main():
    # Validate the arguments
    args = validate_arguments()
    # Create a monitor object and receive messages
    monitor = Monitor(args.type)
    try:
        while True:
            message = monitor.receive()
            datos_json["mensaje"].append(message)
            time.sleep(1)

    except KeyboardInterrupt:
        monitor.subscriber.close()
        monitor.publisher.close()
        monitor.health_informer.close()
        monitor.context.term()
        with open(f'db/datos_monitor_{monitor.topic}.json', 'w') as file:
            json.dump(datos_json, file)
    # end try


# end def


if __name__ == "__main__":
    main()
