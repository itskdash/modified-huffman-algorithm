import os
import ast

def read_message(filename):
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, filename + ".txt")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            message = []
            while True:
                char = file.read(1)
                if char == "":
                    break
                message.append(char)
        return message

    except FileNotFoundError:
        return None

def write_message(message, newname):
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, newname + ".txt")

    with open(filepath, 'w', encoding="utf-8") as file:
        for item in message:
            file.write(str(item))

def read_huffman_compressed(filename):
    folder = os.path.dirname(__file__)
    bitstream_path = os.path.join(folder, filename + ".txt")
    metadata_path = os.path.join(folder, filename + "_metadata.txt")

    try:
        with open(bitstream_path, "r", encoding="utf-8") as file:
            bitstream = file.read()
        with open(metadata_path, "r", encoding="utf-8") as file:
            metadata = ast.literal_eval(file.read())
        return bitstream, metadata

    except FileNotFoundError:
        return None, None

def write_huffman_compressed(bitstream, metadata, newname):
    folder = os.path.dirname(__file__)
    bitstream_path = os.path.join(folder, newname + ".txt")
    metadata_path = os.path.join(folder, newname + "_metadata.txt")

    with open(bitstream_path, "w", encoding="utf-8") as file:
        file.write(bitstream)
    with open(metadata_path, "w", encoding="utf-8") as file:
        file.write(repr(metadata))