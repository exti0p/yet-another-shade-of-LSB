# Yet another shade of LSB

Yet another shade of LSB (YASLSB) technique bridges the well-knowns LSB and PVD steganography approaches together. It can be applied to PNG images.

## How it works

This proof of concept is only working for the green channel at the moment, it hides data using a variant of the LSB steganography. Input data is converted to base2, then for each "0" or "1" to encode, a trick is used. The latter is to alter the image a tiny bit to get the right delta between two following pixels.

For a green pixel `g` and its previous one `pg`, `delta_green = g - pg` can be computed. To encode "0", `delta_green < 0` is set, to encode "1", `delta_green > 0` is set. Hence, for decryption, `delta_green` is evaluated:
    - if it is less than 0, a "0" is encoded.
    - if it is greater than 0, a "1" is encoded.

## Proof of concept with the green channel

I encrypt my data `4n0th3r_cust0m_pr0duct10n`:

```bash
python3 encrypt.py -i images/pepo.png -d 4n0th3r_cust0m_pr0duct10n -o images/encrypted.png
[+] Base2 length data: 200
[+] Successfully encoded plaintext in ./images/encrypted.png
```

Keep in mind that I need that length and it is encoded in the decryption process, I might figure out how automate that in the future. Anyway, I decrypt it:

```bash
python3 decrypt.py -i images/encrypted.png                                                  
[+] Retrieved plaintext from ./images/encrypted.png: 4n6th3r_cust0m_pr0duct10n
```

Voilà! Give it a try yourself by cloning my repository!

## Limitations

Only green channel is supported for encoding at the moment, as a proof of concept.

## Dependency

`sudo pip install pillow`

## Roadmap
- [ ] Add support for encoding into red, blue and alpha channels.
- [ ] Improve accuracy of threshold to encode data to minimize image modification
- [ ] Implement a way to unhide a secret without knowing its size
- [ ] Add support for other kind of images (JPG, GIF...)

## Contributing

Please if you want to bring your stone to the building, read and follow `CONTRIBUTING.md`.