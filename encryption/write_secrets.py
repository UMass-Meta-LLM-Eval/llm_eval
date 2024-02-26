import argparse
import logging
from encryptor import Encryptor


def add_keyval(key, val, path, encryptor):
    enc_val = encryptor.encrypt(val)
    with open(path, 'a') as f:
        f.write(f'{key}={enc_val}\n')


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='secrets.env',
                        help='Path to file to write secrets to')
    parser.add_argument('-k', '--key', default='key.bin',
                        help='Keyfile containing the salt')
    parser.add_argument('params', nargs='*',
                        help='Key-value pairs to write to the file')

    args = parser.parse_args()

    try:
        encryptor = Encryptor.load(args.key)
    except FileNotFoundError:
        logging.warning('Key file not found, generating new key')
        encryptor = Encryptor.generate(args.key)

    for param in args.params:
        key, val = param.split('=', 1)
        add_keyval(key, val, args.path, encryptor)


if __name__ == '__main__':
    main()
