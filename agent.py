import time
import json
import psutil
from kafka import KafkaProducer
from kafka.errors import KafkaError

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'telemetry'

def get_telemetry():
    """Collect system metrics using psutil."""
    cpu_usage = psutil.cpu_percent(interval=None)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": memory_info.percent,
        "memory_used_mb": memory_info.used / (1024 * 1024),
        "disk_usage_percent": disk_info.percent,
        "disk_free_gb": disk_info.free / (1024**3),
        "network_bytes_sent": net_io.bytes_sent,
        "network_bytes_recv": net_io.bytes_recv,
    }

def main():
    print(f"Initializing Kafka Producer linking to {KAFKA_BROKER}...")
    producer = None
    
    # Retry loop for Kafka connection
    while not producer:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Connected to Kafka successfully!")
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    print("Beginning telemetry collection...")
    try:
        while True:
            data = get_telemetry()
            
            try:
                # Send data and wait for a callback
                future = producer.send(KAFKA_TOPIC, data)
                # Block until a single message is sent or timeout
                record_metadata = future.get(timeout=10)
                print(f"Sent telemetry to {record_metadata.topic} partition {record_metadata.partition}: {data}")
            except KafkaError as e:
                print(f"Failed to send data to Kafka: {e}")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping telemetry agent.")
    finally:
        if producer:
            producer.close()

if __name__ == "__main__":
    main()
