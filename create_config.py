import os
import sys


def create_config_dir():
    if sys.platform == 'win32':
        config_dir = os.path.join(os.environ['APPDATA'], 'biobridge')
    elif sys.platform in ['linux', 'darwin']:
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'biobridge')
    else:
        print("Unsupported platform")
        return

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_file = os.path.join(config_dir, 'config.txt')
    if not os.path.exists(config_file):
        open(config_file, 'w').close()


if __name__ == '__main__':
    create_config_dir()
