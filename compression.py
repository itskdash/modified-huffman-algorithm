import math
from huffman_core import calculate_probabilities, build_huffman_tree, generate_huffman_codes

def modified_huffman_compression(message):
    if len(message) == 0:
        raise ValueError("Cannot compress an empty file.")

    frequencies, probabilities = calculate_probabilities(message)

    all_unique_symbols = sorted(list(frequencies.keys()))
    total_unique_count = len(all_unique_symbols)
    
    id_width = max(1, math.ceil(math.log2(total_unique_count)))

    original_codes = {
        char: format(index, f"0{id_width}b")
        for index, char in enumerate(all_unique_symbols)
    }

    grouped_frequencies = {}
    others = []

    for char in frequencies:
        if probabilities[char] < 0.1:
            others.append(char)
        else:
            grouped_frequencies[char] = frequencies[char]

    if len(others) > 0:
        grouped_frequencies["OTHERS"] = sum(frequencies[char] for char in others)

    root = build_huffman_tree(grouped_frequencies)
    codes = generate_huffman_codes(root)

    bitstream = ""
    for char in message:
        if char in others:
            bitstream += codes["OTHERS"] + original_codes[char]
        else:
            bitstream += codes[char]

    metadata = {
        "original_length": len(message),
        "codes": [(symbol, codes[symbol]) for symbol in codes],
        "all_symbols": all_unique_symbols,
        "id_width": id_width
    }

    return bitstream, metadata

def modified_huffman_decompression(bitstream, metadata):
    codes = {code: symbol for symbol, code in metadata["codes"]}
    all_symbols = metadata["all_symbols"]
    id_width = metadata["id_width"]

    original_codes_map = {
        format(index, f"0{id_width}b"): char
        for index, char in enumerate(all_symbols)
    }

    message = []
    current_code = ""
    i = 0

    while i < len(bitstream):
        current_code += bitstream[i]
        i += 1

        if current_code not in codes:
            continue

        symbol = codes[current_code]
        current_code = ""

        if symbol == "OTHERS":
            if i + id_width > len(bitstream):
                raise ValueError("Invalid OTHERS identifier.")

            char_code = bitstream[i:i + id_width]
            i += id_width

            if char_code not in original_codes_map:
                raise ValueError("Invalid OTHERS identifier.")

            message.append(original_codes_map[char_code])
        else:
            message.append(symbol)

    if current_code != "":
        raise ValueError("Invalid Huffman bitstream.")

    if len(message) != metadata["original_length"]:
        raise ValueError("Decoded message length is incorrect.")

    return message