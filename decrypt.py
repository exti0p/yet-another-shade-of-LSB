#!/usr/bin/env python3

from PIL import Image
from optparse import OptionParser

import binascii
import sys


def int2bytes(i: int) -> bytes:
    """
    Converts integer numbers to bytes
    """

    hex_string = "%x" % i
    n = len(hex_string)

    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))


def text_from_bits(bits: str, encoding="utf-8", errors="surrogatepass") -> str:
    """
    Converts base2 numbers (bits) to ASCII text
    """

    n = int(bits, 2)

    return int2bytes(n).decode(encoding, errors)


def decrypt(input_file: str) -> None:
    """
    PoC is only working for the green channel, it hides data using a variant of the LSB steganography.
    Input data is converted to base2, then for each "0" or "1" to encode, a trick is used.
    The latter is to alter the image a tiny bit to get the right delta between two following pixels.

    For a green pixel `g` and its previous one `pg`, delta_green = g - pg can be computed.
    For decryption, delta_green is evaluated:
        - if it is less than 0, a "0" is encoded.
        - if it is greater than 0, a "1" is encoded.
    """

    im = Image.open(input_file)
    pix = im.load()
    width, height = im.size

    data_bin = ""
    # information from encryption
    data_bin_len = 200

    bits_counter = 0

    for h in range(1, height):
        for w in range(1, width, 2):

            # retrieve only data_bin_len bits
            if bits_counter >= data_bin_len:
                # retrieve plaintext by converting from base2 to ascii
                plaintext = text_from_bits(data_bin)
                print(
                    "[+] Retrieved plaintext from {}: {}".format(input_file, plaintext)
                )

                # quits
                raise SystemExit

            red, green, blue = pix[w, h]
            previous_red, previous_green, previous_blue = pix[w - 1, h]

            # delta between current green and previous green
            delta_green = green - previous_green

            if delta_green < 0:
                data_bin += "0"

            elif delta_green > 0:
                data_bin += "1"

            bits_counter += 1


def get_options() -> object:
    parser = OptionParser()

    # required
    parser.add_option(
        "-i",
        "--input-file",
        type="string",
        help="Input file in which data should be hidden.",
    )

    (options, args) = parser.parse_args()

    if len(args) != 0 or not options.input_file:
        parser.print_help()
        raise SystemExit

    return options


if __name__ == "__main__":
    options = get_options()

    decrypt(options.input_file)
