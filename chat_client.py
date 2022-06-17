#!/usr/bin/env python3
from ast import arg
import sys
import threading
import json
import re
from kafka import KafkaProducer, KafkaConsumer
import channel_manager as channelManager
import commandes_manager as commandes

shouldQuit = False
channelsLoaded = ['init']

def read_messages(consumer):
    # TODO À compléter
    while not shouldQuit:
        # On utilise poll pour ne pas bloquer indéfiniment quand should_quit
        # devient True
        global channelsLoaded
        # if channelManager.check_if_refresh():
        channelsLoaded = channelManager.init_or_refresh_channels(consumer, channelsLoaded)
        consumer.subscribe(channelsLoaded)
        received = consumer.poll(100)
        for channel, messages in received.items():
            for msg in messages:
                print("< %s: %s" % (channel.topic, msg.value))





def main_loop(usernameConnected, consumer, producer):
    currentChannel = None
    global channelsLoaded
    while True:
        try:
            if currentChannel is None:
                line = input("> ")
            else:
                line = input("[%s]> " % currentChannel)
        except EOFError:
            print("ERROR")
            line = "/quit"
        if line.startswith("/"):
            cmd, *args = line[1:].split(" ", maxsplit=1)
            cmd = cmd.lower()
            actionArg = None if args == [] else args[0]
        else:
            cmd = "msg"
            actionArg = line
        if cmd == "msg":
            if currentChannel is not None:
                commandes.cmd_msg(producer, currentChannel, actionArg, usernameConnected)
            else:
                print("You should be in a specific channel.")
        elif cmd == "join":
            currentChannel = commandes.cmd_join(consumer, producer, actionArg, channelsLoaded, currentChannel, usernameConnected)
        elif cmd == "part":
            if currentChannel is not None:
                result = commandes.cmd_part(consumer, producer, actionArg, currentChannel, channelsLoaded)
                currentChannel = result["currentChannel"]
                channelsLoaded = result["channelsLoaded"]
            else:
                print("You should be in a specific channel.")
                print("Channel attempt:", actionArg)
        elif cmd == "log":
            commandes.cmd_log(consumer, channelsLoaded)
        elif cmd == "quit":
            commandes.cmd_quit(producer, actionArg)
            break
        # TODO: rajouter des commandes ici



def main():
    if len(sys.argv) != 2:
        return 1

    usernameConnected = sys.argv[1]
    print("Bienvenue sur votre chat", usernameConnected)
    consumer = init_kafka_consumer()
    producer = init_kafka_producer()
    th = threading.Thread(target=read_messages, args=(consumer,))
    th.start()

    try:
        main_loop(usernameConnected, consumer, producer)
    finally:
        global shouldQuit
        shouldQuit = True
        th.join()

def init_kafka_consumer():
    return KafkaConsumer(bootstrap_servers=['localhost:9092'])

def init_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=['localhost:9092'],\
        value_serializer=lambda v: json.dumps(v).encode('utf-8')\
    )

if __name__ == "__main__":
    sys.exit(main())
