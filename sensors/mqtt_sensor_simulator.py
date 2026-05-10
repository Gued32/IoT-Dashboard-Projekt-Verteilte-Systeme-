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
            if not client.is_connected():
                print("MQTT client disconnected, attempting reconnect...")
                try:
                    client.reconnect()
                except OSError as error:
                    print(f"Reconnect failed: {error}")
                    time.sleep(args.interval)
                    continue

            payload = generate_payload(args.sensor_id)
            data = json.dumps(payload)
            message_info = client.publish(args.topic, data)
            publish_timeout = min(2.0, max(0.5, args.interval * 0.8))
            message_info.wait_for_publish(timeout=publish_timeout)
            if message_info.is_published():
                print(f"Published to {args.topic}: {data}")
            else:
                print(
                    "Publish failed for topic "
                    f"{args.topic} ({mqtt.error_string(message_info.rc)}): {data}"
                )
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
