#!/usr/bin/env python

import asyncio
import logging
import shutil
import socket

import configargparse

from markov import Markov
from time import time

logging.basicConfig(level=logging.INFO)

parser = configargparse.ArgParser(description="Robots: A triumph of machine over man")
parser.add_argument(
    "-c", "--config", is_config_file=True, help="Path to config file in yaml format"
)

parser.add_argument(
    "--local_server_port",
    type=int,
    help="Set a local listen port to enable a local server",
)
parser.add_argument(
    "-b",
    "--brain",
    env_var="BOT_BRAIN",
    required=True,
    help="This bot's input brain as a YAML or newline-delimited text file, also used as the base name for rotated brains",
)
parser.add_argument(
    "-o",
    "--output",
    env_var="BOT_OUTPUT",
    required=True,
    help="File for writing the real-time updated corpus",
)
parser.add_argument(
    "-n",
    "--name",
    env_var="BOT_NAME",
    required=True,
    help="The name this bot will respond to in chats",
)
parser.add_argument(
    "-r",
    "--rotate",
    env_var="CB_ROTATE",
    required=False,
    action="store_true",
    help="Backup the brain and copy the output to the brain on SIGTERM",
)
args = parser.parse_args()

bot_name = args.name
brain = Markov(input_file=args.brain, output_file=args.output, ignore_words=[bot_name])

def rotate_brain(the_brain: str, output: str):
    brain_backup = "{}.{}".format(the_brain, time())
    shutil.move(the_brain, brain_backup)
    shutil.move(output, the_brain)


def sanitize_and_tokenize(msg: str) -> list:
    msg_tokens = msg.split()
    for i in range(0, len(msg_tokens)):
        msg_tokens[i] = msg_tokens[i].strip("'\"!@#$%^&*().,/\\+=<>?:;").upper()
    return msg_tokens

def get_ten() -> str:
    response = ""
    for i in range(0, 9):
        response += brain.create_response()
        response += "\n"
    return response

def create_raw_response(incoming_message):
    msg_tokens = sanitize_and_tokenize(incoming_message)
    if (bot_name.upper() in msg_tokens) or "TOWN" in msg_tokens:  # it's not _not_ a bug
        if "GETGET10" in msg_tokens:
            return get_ten()
        else:
            return brain.create_response(incoming_message, learn=True)

def run_local_server(port_num):
    host = "localhost"
    port = port_num
    prompt = "\nSay something: "
    print("Listening on port: " + str(port))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print("Connection recieved from", addr)
            while True:
                conn.sendall(str.encode(prompt))
                data = conn.recv(1024)
                if not data:
                    break
                decoded_data = data.decode("utf-8")
                response = create_raw_response(decoded_data)
                if response:
                    response = bot_name + " " + "said: " + response
                    conn.sendall(str.encode(response))

def main():
    basic_loop = asyncio.get_event_loop()
    try:
        if args.local_server_port:
            run_local_server(port_num=args.local_server_port)
        basic_loop.run_forever()
    except KeyboardInterrupt:
        if args.rotate:
            rotate_brain(args.brain, args.output)
    finally:
        basic_loop.close()

if __name__ == '__main__':
    main()
