# PNG Steganography CLI

PNG Steganography CLI is a command-line tool that allows you to hide a message within a PNG image using steganography techniques. It also incorporates a simple RSA encryption algorithm to encrypt the hidden message for added security.

Steganography is the practice of concealing information within other non-secret data to avoid detection. In this tool, a message is hidden by modifying the pixel data of a PNG image, making it appear unchanged to the human eye while containing the hidden information. When hiding a message, you can choose the number of bits to alter in each byte of the image. The available options are 1 to 4 bits. Using a higher number of bits provides more space for the message but also increases the chances of the alteration being detected.

The RSA encryption algorithm is a widely used public-key encryption method that utilizes the properties of prime numbers for secure data transmission. The hidden message is encrypted using a randomly generated public-private key pair, ensuring that only the intended recipient with the corresponding private key can decrypt and extract the message.

__Note__: The prime numbers used for generating RSA key pairs in this tool are not large enough for secure production use. They are provided for demonstration purposes only. For real-world applications, it is crucial to use much larger prime numbers to ensure the security of the encryption.

## Features

- Hide a message within a PNG image
- Extract a hidden message from a PNG image

## Requirements

- Python 3.6+
- NumPy library
- PIL (Python Imaging Library) library

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/png-steganography-cli.git# PNG Steganography CLI

2. Navigate to the project directory:
   ```bash
   cd png-steganography-cli
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Usage
```bash
python3 png_steganography.py hide <source_image> <data_file> [--bits <num_bits>] [--output <output_image>]
```
* __hide__: Action to hide a message within a PNG image.
* __&lt;source_image&gt;__: Path to the source PNG image.
* __&lt;data_file&gt;__: Path to the file containing the message to be hidden
* __--bits &lt;num_bits&gt;__(optional): Number of bits to alter in each byte(1-4). Default is 1.
* __--output &lt;output_file&gt;__(optional): Output path for the new image. If not provided, the soruce image will be overwritten.

``` bash
python3 png_steganography.py extract <source_image> <decryption_key> [--bits <num_bits>] [--output <output_file>]
```
* __extract__: Action to extract a hidden message from a PNG image.
* __&lt;source_image&gt;__: Path to the PNG image that stores the hidden message.
* __&lt;decryption_key&gt;__: Decryption key used to extract the message.
* __--bits &lt;num_bits&gt;__(optional): Number of bits used when the image was altered(1-4). Default is 1.
* __--output &lt;output_file&gt;__(optional): Path to a file where the extracted message should be saved. If not provided, the message will be printed to the console.

## Examples
* Hiding a message within an image:
  ``` bash
  python3 png_steganography.py hide image.png secret.txt --bits 2 --output output.png
  ```
* Extracting a hidden message from an image:
  ``` bash
  python3 png_steganography.py extract image.png 12345-6789 --bits 2 --output extracted.txt
  ```

  ### Hiding Romeo & Juliet inside an Image.
  This is an example of the whole novel Romeo & Juliet hidden inside an image.

  The original image looks like this:
  ![landscape](https://github.com/alexandengstrom/png-steganography-cli/assets/123507241/1099914d-fd33-4bac-9ccb-db5e764ba008)

  This is the same message with Romeo & Juliet hidden inside. This image is only using one bit in every byte which is the least significant bit. This means its impossible for a human eye to see any difference:
  ![encoded1](https://github.com/alexandengstrom/png-steganography-cli/assets/123507241/6138d048-b854-4f3a-8969-610956bcb4be)

  If we instead choose to use the last four bits of every byte we can see some small changes in the sky:
  ![encoded4](https://github.com/alexandengstrom/png-steganography-cli/assets/123507241/36924519-d143-48c3-bf65-418d322c64da)

