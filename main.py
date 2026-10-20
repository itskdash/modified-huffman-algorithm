from io_utils import (
    read_message,
    write_message,
    read_huffman_compressed,
    write_huffman_compressed
)
from compression import (
    modified_huffman_compression,
    modified_huffman_decompression
)

def run_app():
    print(
        "\n┌─────────────────────────┐"
        "\n│       | Welcome |       │"
        "\n│  Data Compression App   │"
        "\n└─────────────────────────┘"
    )

    while True:
        print(
            "\n┌─────────────────────────┐"
            "\n│   [ Modified Huffman ]  │"
            "\n├─────────────────────────┤"
            "\n│  [1]  Compression       │"
            "\n│  [2]  Decompression     │"
            "\n│  [0]  Exit              │"
            "\n└─────────────────────────┘"
        )

        try:
            choice = int(input("Please enter your choice: "))

            if choice == 1:
                filename = input("Please enter file name: ").strip()
                message = read_message(filename)

                if message is None:
                    print("File not found please enter a valid file name.")
                else:
                    bitstream, metadata = modified_huffman_compression(message)
                    newname = input("Enter new file name: ").strip()
                    write_huffman_compressed(bitstream, metadata, newname)

                    print("File created successfully!")
                    print("Compressed file:", newname + ".txt")
                    print("Metadata file:", newname + "_metadata.txt")

            elif choice == 2:
                filename = input("Please enter compressed file name: ").strip()
                bitstream, metadata = read_huffman_compressed(filename)

                if bitstream is None or metadata is None:
                    print("File not found please enter a valid file name.")
                else:
                    message = modified_huffman_decompression(bitstream, metadata)
                    newname = input("Enter new file name: ").strip()
                    write_message(message, newname)
                    print("File decompressed successfully!")

            elif choice == 0:
                print("\nGoodbye!")
                break

            else:
                print("Invalid choice please try again.")

        except (ValueError, SyntaxError, KeyError, TypeError) as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_app()