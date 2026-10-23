def calculate_probabilities(message):
    frequencies = {}
    total = len(message)

    for char in message:
        frequencies[char] = frequencies.get(char, 0) + 1

    probabilities = {char: frequencies[char] / total for char in frequencies}

    return frequencies, probabilities

def build_huffman_tree(frequencies):
    nodes = []
    order = 0

    for symbol in frequencies:
        nodes.append((frequencies[symbol], order, symbol))
        order += 1

    while len(nodes) > 1:
        min_index = 0
        for i in range(1, len(nodes)):
            if nodes[i][0] < nodes[min_index][0]:
                min_index = i
        first = nodes.pop(min_index)

        min_index = 0
        for i in range(1, len(nodes)):
            if nodes[i][0] < nodes[min_index][0]:
                min_index = i
        second = nodes.pop(min_index)

        parent = (first[2], second[2])
        nodes.append((first[0] + second[0], order, parent))
        order += 1

    return nodes[0][2]

def generate_huffman_codes(root):
    codes = {}
    stack = [(root, "")]

    while stack:
        node, code = stack.pop()

        if not isinstance(node, tuple):
            codes[node] = "0" if code == "" else code

        else:
            left = node[1]
            right = node[0]
            stack.append((right, code + "1"))
            stack.append((left, code + "0"))

    return codes