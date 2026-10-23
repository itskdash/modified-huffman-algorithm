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
    bitstream_path = os.path.join(folder, filename + ".bin")
    metadata_path = os.path.join(folder, filename + "_metadata.txt")

    try:
        with open(metadata_path, "r", encoding="utf-8") as file:
            metadata = ast.literal_eval(file.read())

        with open(bitstream_path, "rb") as file:
            bytes_data = file.read()

        bitstream = "".join(f"{byte:08b}" for byte in bytes_data)

        extra_padding = metadata.get('extra_padding', 0)
        if extra_padding > 0:
            bitstream = bitstream[:-extra_padding]

        return bitstream, metadata

    except FileNotFoundError:
        return None, None

def write_huffman_compressed(bitstream, metadata, newname):
    folder = os.path.dirname(__file__)
    bitstream_path = os.path.join(folder, newname + ".bin")
    metadata_path = os.path.join(folder, newname + "_metadata.txt")

    extra_padding = (8 - len(bitstream) % 8) % 8
    bitstream += '0' * extra_padding

    metadata['extra_padding'] = extra_padding

    byte_array = bytearray()
    for i in range(0, len(bitstream), 8):
        byte = bitstream[i:i+8]
        byte_array.append(int(byte, 2))

    with open(bitstream_path, "wb") as file:
        file.write(byte_array)

    with open(metadata_path, "w", encoding="utf-8") as file:
        file.write(repr(metadata))