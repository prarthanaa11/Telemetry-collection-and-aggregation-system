import json
import time
from datetime import datetime, timezone
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Kafka Config
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'telemetry'

# InfluxDB Config
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-token"
INFLUXDB_ORG = "my-org"
INFLUXDB_BUCKET = "telemetry_bucket"

def connect_to_kafka():
    """Connect to Kafka with retries."""
    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='telemetry-consumer-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print("Connected to Kafka successfully!")
            return consumer
        except Exception as e:
            print(f"Kafka connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def connect_to_influxdb():
    print(f"Connecting to InfluxDB at {INFLUXDB_URL}...")
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    
    # Simple check to guarantee it's online
    while True:
        try:
            if client.ping():
                print("Connected to InfluxDB successfully!")
                return client
        except Exception as e:
            pass
        print("InfluxDB not ready. Retrying in 5 seconds...")
        time.sleep(5)

def main():
    consumer = connect_to_kafka()
    influx_client = connect_to_influxdb()
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    # State for rolling metrics
    cpu_history = []
    peak_cpu = 0.0

    print("Listening for telemetry messages...")
    try:
        for message in consumer:
            data = message.value
            current_time = datetime.now(timezone.utc)
            
            # Extract CPU
            current_cpu = data.get("cpu_usage_percent", 0.0)
            
            # Update peak computation
            if current_cpu > peak_cpu:
                peak_cpu = current_cpu
                
            # Update rolling average (last 10 values)
            cpu_history.append(current_cpu)
            if len(cpu_history) > 10:
                cpu_history.pop(0)
            rolling_avg_cpu = sum(cpu_history) / len(cpu_history)

            # Build InfluxDB Point
            point = (
                Point("system_telemetry")
                .tag("host", "agent-1")
                .field("cpu_usage_percent", current_cpu)
                .field("cpu_rolling_avg", rolling_avg_cpu)
                .field("cpu_peak", peak_cpu)
                .field("memory_usage_percent", data.get("memory_usage_percent", 0.0))
                .field("memory_used_mb", data.get("memory_used_mb", 0.0))
                .field("disk_usage_percent", data.get("disk_usage_percent", 0.0))
                .field("network_bytes_sent", data.get("network_bytes_sent", 0.0))
                .field("network_bytes_recv", data.get("network_bytes_recv", 0.0))
                .time(current_time, WritePrecision.NS)
            )

            try:
                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
                print(f"[{current_time.isoformat()}] Processed & Stored: CPU {current_cpu}% (Avg: {rolling_avg_cpu:.1f}%, Peak: {peak_cpu}%)")
            except Exception as e:
                print(f"Failed to write to InfluxDB: {e}")

    except KeyboardInterrupt:
        print("\nStopping telemetry consumer.")
    finally:
        consumer.close()
        write_api.close()
        influx_client.close()

if __name__ == "__main__":
    main()
