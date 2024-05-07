import redis
import json

# Connect to Redis server
redis_host = 'localhost'  # Cambia al host de Redis
redis_port = 6379  # Cambia al puerto especifico
redis_password = ""  # Usa la contrasena especificada

# Se crea el cliente
redis_client = redis.Redis(host=redis_host, 
                           port=redis_port, 
                           password=redis_password)

list_name = 'communications_logs_queue'
def push_to_list(item):
    redis_client.rpush(list_name, item)

# Uso de ejemplo
if __name__ == "__main__":
    example_requests = [ {'datetime':'2024-02-19 5:00:00',
                          'caller_service_id': 4,
                          'receiver_service_id': 1,
                          'status_code': 202,
                          'latency_ms': 100}, 
                        ]

    for request in example_requests:
        #json dumps convierte de diccionario a string
        push_to_list(json.dumps(request))

    print(f"Información enviada exitosamente a la lista {list_name}.")