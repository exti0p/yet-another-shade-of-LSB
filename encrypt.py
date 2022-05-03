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


def text_to_bits(text: str, encoding="utf-8", errors="surrogatepass") -> str:
    """
    Converts ASCII text to base2 numbers (bits)
    """

    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]

    return bits.zfill(8 * ((len(bits) + 7) // 8))


def encrypt(input_file: str, data: str, output_file: str) -> None:
    """
    PoC is only working for the green channel, it hides data using a variant of the LSB steganography.
    Input data is converted to base2, then for each "0" or "1" to encode, a trick is used.
    The latter is to alter the image a tiny bit to get the right delta between two following pixels.

    For a green pixel `g` and its previous one `pg`, delta_green = g - pg can be computed.
    To encode "0", delta_green < 0 is set, to encode "1", delta_green > 0 is set.
    """

    # threshold found to limit image modification while encrypting successfully
    THRESHOLD = 3

    # input image
    im = Image.open(input_file)
    pix = im.load()
    width, height = im.size

    # retrieve data and convert from ascii to base2
    data_bin = text_to_bits(data)
    data_bin_len = len(data_bin)

    print("[+] Base2 length data: {}".format(data_bin_len))

    bits_counter = 0

    # start from pixel 0 to encode from pixel 1
    for h in range(1, height):
        for w in range(1, width, 2):

            # we need data_bin_len encoded
            if bits_counter >= data_bin_len:
                # no more encoding needed, exits and saves image
                print("[+] Successfully encoded plaintext in {}".format(output_file))

                # save modified image
                im.save(output_file)

                # quits
                raise SystemExit

            red, green, blue = pix[w, h]
            previous_red, previous_green, previous_blue = pix[w - 1, h]

            # delta between current green and previous green
            delta_green = green - previous_green

            if data_bin[bits_counter] == "0":
                # modifying pixels to get delta_green < 0

                if delta_green > 0:
                    if previous_green != 0:
                        THRESHOLD = green // previous_green
                        previous_green += 3 * THRESHOLD
                    else:
                        THRESHOLD = green // (previous_green + 1)
                        previous_green += 3 * THRESHOLD

                elif delta_green < 0:
                    pass

                # delta_green == 0
                else:
                    previous_green += 1

                delta_green = green - previous_green

                if delta_green < 0:
                    # pixel modifying went fine
                    pass
                else:
                    raise Exception("[-] Pixel modifying went WRONG")

                # red green blue
                pix[w, h] = (red, green + delta_green, blue)

            elif data_bin[bits_counter] == "1":
                # modifying pixels to get delta_green > 0

                if delta_green > 0:
                    pass

                elif delta_green < 0:
                    if green != 0:
                        THRESHOLD = previous_green // green
                        green += 3 * THRESHOLD
                    else:
                        THRESHOLD = previous_green // (green + 1)
                        green += 3 * THRESHOLD

                # delta_green == 0
                else:
                    green += 1

                delta_green = green - previous_green

                if delta_green > 0:
                    # pixel modifying went fine
                    pass
                else:
                    raise Exception("[-] Pixel modifying went WRONG")

                # red green blue
                pix[w, h] = (red, green + delta_green, blue)

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
    parser.add_option(
        "-d", "--data", type="string", help="Data (represented as string) to hide."
    )
    # optional
    parser.add_option(
        "-o",
        "--output-file",
        type="string",
        default="encrypted.png",
        help="Name of the output file containing the hidden data.",
    )

    (options, args) = parser.parse_args()

    if len(args) != 0 or not options.input_file or not options.data:
        parser.print_help()
        raise SystemExit

    return options


if __name__ == "__main__":
    options = get_options()

    encrypt(options.input_file, options.data, options.output_file)
