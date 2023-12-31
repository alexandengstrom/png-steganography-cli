import numpy as np
import PIL.Image
import random
import argparse
import json
import sys

def read_content(path):
    """
    Reads the content of a file.

    Args:
        path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    
    try:
        with open(path, "r") as data:
            return data.read()
    except:
        print(f"ERROR: Failed to read from {path}", file=sys.stderr)
        exit()

def hide_message(message, png, output, pubkey, bit_len=1):
    """
    Hides a message inside a PNG image.

    Args:
        message (str): The message to be hidden.
        png (str): Path to the source PNG file.
        output (str): Output path for the new image.
        pubkey (tuple): Public key for encryption.
        bit_len (int): Number of bits to alter in each byte (1-4).

    Returns:
        None
    """

    image = PIL.Image.open(png, "r")
    width, height = image.size
    img_data = np.array(list(image.getdata()))
    pixels = img_data.size
    channels = 4 if image.mode == "RGBA" else 3

    encrypted_message = encrypt(pubkey, message)
    bit_string = "".join(bin(num)[2:].zfill(32) for num in encrypted_message)
    bit_string += "".join(f"{ord(c):08b}" for c in "$EOT$")
    
    bits_needed = len(bit_string)
    avai_bits = int((pixels * bit_len) / 4 * 3 if channels == 4 else pixels * bit_len)

    print("Image inspected, requirements:")
    print(f"{'Needed:'.ljust(15)} {str(bits_needed).ljust(10)} bits")
    print(f"{'Available:'.ljust(15)} {str(avai_bits).ljust(10)} bits")

    if bits_needed > avai_bits:
        print(f"\nERROR: Message to large to fit inside {png}", file=sys.stderr)
        print(f"Overflow: {bits_needed-avai_bits} bits", file=sys.stderr)
        exit()

    index = 0
    for i in range(pixels):
        if index >= bits_needed:
            break
        for j in range(0, 3):
            if index < bits_needed:
                tmp = (img_data[i][j] & ~(2 ** bit_len - 1))
                img_data[i][j] = tmp | int(bit_string[index:(index+bit_len)], 2)
                index += bit_len

    img_data = img_data.reshape((height, width, 4 if image.mode == "RGBA" else 3))
    result = PIL.Image.fromarray(img_data.astype("uint8"), image.mode)

    result.save(png) if not output else result.save(output)

def extract_message(png, seckey, bytes_len=1):
    """
    Extracts a hidden message from a PNG image.

    Args:
        png (str): Path to the PNG file that stores the message.
        seckey (tuple): Decryption key.
        bytes_len (int): Number of bits used when the image was altered (1-4).

    Returns:
        str: The extracted message.
    """
    
    image = PIL.Image.open(png, "r")
    img_data = np.array(list(image.getdata()))
    
    secret_bits = ""
    for i in range(img_data.size // 4 if image.mode == "RGBA" else 3):
        for j in range(3):
            for k in range(8-bytes_len, 8):
                secret_bits += format(img_data[i][j], '08b')[k]

    split_bits = secret_bits.split(''.join(format(ord(c), '08b') for c in "$EOT$"))[0]
    int_list = [int(split_bits[i:i+32], 2) for i in range(0, len(split_bits), 32)]

    return decrypt(seckey, int_list)

def generate_primes():
    """
    Generates two prime numbers.

    Returns:
        tuple: Two randomly generated prime numbers.
    """
    
    try:
        with open("primes.json", "r") as data:
            data = json.load(data)
            return random.sample(data, 2)
    except FileNotFoundError:
        print("Could not find primes.json, the file is required for generating keypairs", file=sys.stderr)
        exit()

def text2ints(text, m):
    """
    Converts text into a list of integers.

    Args:
        text (str): The text to convert.
        m (int): The block size.

    Returns:
        list: The list of integers representing the text.
    """
    
    #t = text.encode()
    t = text.encode()
    t += b"\x00" * ((m - len(t) % m) % m)
    return [int.from_bytes(t[i:i+m], "big") for i in range(0, len(t), m)]

def ints2text(ints, m):
    """
    Converts a list of integers into text.

    Args:
        ints (list): The list of integers to convert.
        m (int): The block size.

    Returns:
        str: The converted text.
    """
    
    try:
        return (b"".join(i.to_bytes(m, "big") for i in ints).split(b"\x00")[0]).decode()
    except OverflowError:
        print("ERROR: Failed to decrypt the message, verify your decryption key", file=sys.stderr)
        exit()

def generate_keypair(p, q):
    """
    Generates a key pair for encryption and decryption.

    Args:
        p (int): The first prime number.
        q (int): The second prime number.

    Returns:
        tuple: Public key and private key.
    """
    
    n = p * q
    phi = (p-1) * (q-1)

    e = random.randint(2, phi-1)
    while gcd(e, phi) != 1:
        e = random.randint(2, phi-1)
       
    d = xgcd(e, phi)[1] % phi

    return (e, n), (d, n)

def encrypt(pubkey, plaintext):
    """
    Encrypts plaintext using the public key.

    Args:
        pubkey (tuple): Public key for encryption.
        plaintext (str): The plaintext to encrypt.

    Returns:
        list: The encrypted message as a list of integers.
    """
    
    b = find_blocksize(pubkey[1])
    return [pow(i, pubkey[0], pubkey[1]) for i in text2ints(plaintext, b)]


def decrypt(seckey, ciphertext):
    """
    Decrypts ciphertext using the private key.

    Args:
        seckey (tuple): Decryption key.
        ciphertext (list): The ciphertext to decrypt.

    Returns:
        str: The decrypted message.
    """
    
    b = find_blocksize(seckey[1])
    return ints2text([pow(i, seckey[0], seckey[1]) for i in ciphertext], b)

def find_blocksize(n):
    """
    Finds the block size based on the given number.

    Args:
        n (int): The number to find the block size for.

    Returns:
        int: The block size.
    """
    
    b = 1
    while pow(2, (8*(b+1)))-1 < n:
        b += 1
        
    return b

def xgcd(a, b):
    """
    Extended Euclidean algorithm to calculate the greatest common divisor (GCD).

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        tuple: GCD and coefficients x, y.
    """
    
    if b == 0:
        g, x, y = a, 1, 0
    else:
        g, y, x = xgcd(b, a % b)
        y -= x * (a // b)
        
    return g, x, y

def gcd(a, b):
    """
    Calculates the greatest common divisor (GCD) of two numbers.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The GCD of the two numbers.
    """
    
    return a if b == 0 else gcd(b, a % b)

def setup_argparser():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    
    parser = argparse.ArgumentParser(description="Hide or extract a message from a PNG image.")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform: hide or extract")

    hide_parser = subparsers.add_parser("hide",
                                        help="Hide a message in a PNG image")
    hide_parser.add_argument("source",
                             type=str,
                             help="Path to the source PNG file")
    
    hide_parser.add_argument("data",
                             type=str,
                             help='The file to hide')
    
    hide_parser.add_argument("--bits",
                             type=int,
                             choices=range(1, 5),
                             default=1,
                             help="Number of bits to alter in each byte (1-4)")
    
    hide_parser.add_argument("--output",
                             type=str,
                             help="Output path for the new image")

    extract_parser = subparsers.add_parser("extract",
                                           help="Extract a message from a PNG image")
    
    extract_parser.add_argument("source",
                                type=str,
                                help="Path to the PNG file that stores the message")
    
    extract_parser.add_argument("key",
                                type=str,
                                help="Decryption key")
    
    extract_parser.add_argument("--bits",
                                type=int,
                                choices=range(1, 5),
                                default=1,
                                help="Number of bits used when the image was altered (1-4)")

    extract_parser.add_argument("--output",
                             type=str,
                             help="Path to a file where the message should be saved")

    return parser

if __name__ == "__main__":
    args = setup_argparser().parse_args()

    if args.action == "hide":
        data = read_content(args.data)
        output_path = args.output if args.output else args.source
        prime1, prime2 = generate_primes()
        pubkey, seckey = generate_keypair(prime1, prime2)
        hide_message(data, args.source, output_path, pubkey, args.bits)
        print()
        print(f"Message was hidden inside {output_path} succesfully!")
        print(f"Decryption key: {str(seckey[0])}-{str(seckey[1])}")
    elif args.action == "extract":
        seckey = (int(args.key.split("-")[0]), int(args.key.split("-")[1]))
        message = extract_message(args.source, seckey, args.bits)

        if args.output:
            with open(args.output, "w") as filename:
                filename.write(message)
        else:
            print(message)
