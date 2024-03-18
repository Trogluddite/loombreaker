import subprocess
import os

SEED_FILE = '/home/mpappas/apache-nutch-1.19/urls/seed.txt'
SEED_TEXT = 'https://forgefit24.com'

def main():

    fp = open(SEED_FILE, "w")
    fp.write(SEED_TEXT)
    fp.close()

if __name__ == '__main__':
    main()
