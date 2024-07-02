import logging
import asyncio
import os
from amqtt.broker import Broker
from amqtt.client import MQTTClient
from authentication import authentication

from amqtt.codecs import int_to_bytes_str
from amqtt.mqtt.constants import QOS_1, QOS_2

config = {
    "listeners": {
        "default": {
            "bind": "127.0.0.1:1883",
            "type": "tcp",
            "max_connections": 10,
        },
    },
    "auth": {
        "allow-anonymous": False,
        "plugins": ["auth_file", "auth_anonymous"],
        "password-file": os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "client_password.txt"
        ),
    },
    "topic-check": {
        "enabled": True,
        "plugins": ["topic_acl", "topic_taboo"],
        "acl": {
            "auth_handler": ["AUTH_REQ/#", "AUTH_RET/#"],
        },
    },
}

broker = Broker(config)

async def broker_coro():
    await broker.start()
    
    try:
        c = MQTTClient()
        await c.connect("mqtt://auth_handler:auth_handler@127.0.0.1:1883")
        await c.subscribe([("AUTH_REQ/#", QOS_1)])
        while True:
            message = await c.deliver_message()
            print("new message")
            packet = message.publish_packet
            topic_name = packet.variable_header.topic_name
            payload = str(packet.payload.data)[12:-2]
            print(topic_name[0:9], payload, topic_name[9:14])

            if topic_name[0:9] == "AUTH_REQ/":
                username, password = payload.split(", ")
                auth = authentication(username, password)
                result, client = auth.start_client()
                await c.publish(f"AUTH_RET/{topic_name[9:14]}", int_to_bytes_str(result), qos=0x00)
    except ConnectionError:
        asyncio.get_event_loop().stop()
    
if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)
    asyncio.get_event_loop().run_until_complete(broker_coro())
    asyncio.get_event_loop().run_forever()