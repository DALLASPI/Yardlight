#!/usr/bin/env python 3

from main import *

def setup():
    Light.default_setup()
def main():
    Light.main()
def destroy():
    Light.destroy()

try:
    if __name__ == '__main__':
        setup()
        main()
except KeyboardInterrupt:
    destroy()
