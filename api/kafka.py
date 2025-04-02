from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

def create_kafka_clients():
    try:
        producer = Producer({
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "transactional.id": "todo-producer",
            "enable.idempotence": True,
        })
        producer.init_transactions()

        admin_client = AdminClient({
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
        })
        new_topic = NewTopic(topic=KAFKA_TOPIC, num_partitions=1, replication_factor=1)
        fs = admin_client.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Топик '{topic}' создан.")
            except Exception as e:
                print(f"Не удалось создать топик '{topic}': {e}")

        return producer

    except:
        print(f"Ошибка подключения к Kafka, работаем без него.")
        return None, None


producer = create_kafka_clients()