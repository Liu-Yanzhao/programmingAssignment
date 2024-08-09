# Author: Liu Yanzhao
# Admin No / Grp: 240333N / AA2402
# Copyright (c) 2024 yamgao_

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Importing required libraries
import os
import json
import logging
import asyncio
from amqtt.broker import Broker
from amqtt.client import MQTTClient

# Importing user-defined libraries
from src.admin import admin
from src.authentication import authentication

# Importing important server functions
from amqtt.codecs import int_to_bytes_str
from amqtt.mqtt.constants import QOS_1, QOS_2

# Configuration for AMQTT server
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
            os.path.dirname(os.path.realpath(__file__)), "src/server_client_password.txt"
        ),
    },
    "topic-check": {
        "enabled": True,
        "plugins": ["topic_acl", "topic_taboo"],
        "acl": {
            "auth_handler": ["AUTH_REQ/#", "AUTH_RET/#", "DATA_REQ/#", "DATA_RET/#", "DATA_PUB/#", "DATA_NEW/#", "DATA_ERROR/#", "DATA_DEL/#"],
        },
    },
}

# creating amqtt broker class
broker = Broker(config)

async def broker_coro():
    """
    asynchronous function to subscribed to and publish AMQTT messages
    """
    await broker.start()  # wait for broker to start
    
    try:
        c = MQTTClient()
        adminClient = admin()
        await c.connect("mqtt://auth_handler:auth_handler@127.0.0.1:1883")  # connect broker client to broker
        await c.subscribe([  # subscribe to 5 topics
            ("AUTH_REQ/#", QOS_1),
            ("DATA_REQ/#", QOS_1),
            ("DATA_PUB/#", QOS_1),
            ("DATA_NEW/#", QOS_1),
            ("DATA_DEL/#", QOS_1)
            ])
        while True:  # loop to continuously receive process and send messages
            message = await c.deliver_message() # wait until message is received
            packet = message.publish_packet  # get packet payload
            topic_name = packet.variable_header.topic_name  # get MQTT topic
            payload = str(packet.payload.data)[12:-2]  # get payload

            if topic_name[0:9] == "AUTH_REQ/":  # if topic is authentication request
                username, password = payload.split(", ")  # retrieve username and password
                auth = authentication(username, password)  # initialise authentication class
                result = auth.return_result()  # get authentication result
                await c.publish(f"AUTH_RET/{topic_name[9:14]}", int_to_bytes_str(result), qos=0x00)  # return authentication result back to client

            elif topic_name[0:9] == "DATA_REQ/":  # if topic is data request
                adminClient.retrieve_products()  # retrieve data from json file
                await c.publish(f"DATA_RET/{topic_name[9:14]}", int_to_bytes_str(json.dumps(adminClient.products)), qos=0x00)  # send data back to client

            elif topic_name[0:9] == "DATA_PUB/":  # if topic is requesting to change payload
                new_data = json.loads(payload)  # turning payload into a json
                error = adminClient.change_product(new_data["Product ID"], {  # changing product which returns any errors 
                    "Product Name": new_data["Product Name"],
                    "Category": new_data["Category"],
                    "Description": new_data["Description"],
                    "Price": new_data["Price"],
                    "Quantity Available": new_data["Quantity Available"]
                })
                await c.publish(f"DATA_ERROR/{topic_name[9:14]}", int_to_bytes_str(error), qos=0x00)  # publishing back any errors to client

            elif topic_name[0:9] == "DATA_NEW/":  # if topic is requesting for new data
                new_data = json.loads(payload)  # turning payload in json
                error = adminClient.new_product(  # adding new product which returns any errors
                    new_data["Product ID"], 
                    new_data["Product Name"],
                    new_data["Category"],
                    new_data["Description"],
                    new_data["Price"],
                    new_data["Quantity Available"]
                )
                await c.publish(f"DATA_ERROR/{topic_name[9:14]}", int_to_bytes_str(error), qos=0x00)  # publishing back any errors to client

            elif topic_name[0:9] == "DATA_DEL/":  # if topic is deleting data
                adminClient.remove_product(payload)  # delete product

    except ConnectionError:  # if there is any connection error
        asyncio.get_event_loop().stop()  # stop server

# Run code
if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)  # for logging
    asyncio.get_event_loop().run_until_complete(broker_coro())  # to run asyncronous function forever
    asyncio.get_event_loop().run_forever()  # to run asyncronous function forever