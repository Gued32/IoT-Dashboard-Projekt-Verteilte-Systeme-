import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


def generate_payload(sensor_id: str) -> dict:
    return {
        "sensor_id": sensor_id,
        "temperature": round(random.uniform(18.0, 30.0), 2),
        "humidity": round(random.uniform(30.0, 80.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MQTT sensor simulator")
    parser.add_argument("--broker", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--topic", default="sensors/data", help="MQTT topic")
    parser.add_argument("--sensor-id", default="sensor-1", help="Sensor ID")
    parser.add_argument(
        "--interval", type=int, default=5, help="Publish interval in seconds"
    )
    args = parser.parse_args()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=args.sensor_id,
    )
    try:
        client.connect(args.broker, args.port, 60)
    except OSError as error:
        print(
            f"Could not connect to MQTT broker at {args.broker}:{args.port} ({error})."
        )
        sys.exit(1)
    client.loop_start()

    try:
        while True:
            payload = generate_payload(args.sensor_id)
            data = json.dumps(payload)
            message_info = client.publish(args.topic, data)
            if message_info.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to {args.topic}: {data}")
            else:
                print(
                    f"Publish failed for topic {args.topic} with rc={message_info.rc}: {data}"
                )
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
