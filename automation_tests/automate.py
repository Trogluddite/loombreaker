import subprocess
import os

NUTCH_HOME = '/home/mpappas/apache-nutch-1.19'
CRAWL_DIR = '/home/mpappas/apache-nutch-1.19/crawl'
SEED_FILE = '/home/mpappas/apache-nutch-1.19/urls/seed.txt'
NUM_ROUNDS = 1 #Need to eventually allow an argument

def main():
    #Initialize Crawl
    subprocess.run([f"{NUTCH_HOME}/bin/nutch", "inject", f"{CRAWL_DIR}/crawldb", SEED_FILE], check=True)

    #Run Crawler
    for i in range(1, NUM_ROUNDS + 1):
        print(f"Crawl Round: {i}")
        #Generate Fetch List
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "generate", f"{CRAWL_DIR}/crawldb", f"{CRAWL_DIR}/segments"], check=True)
        #Find latest segment
        segments_dir = os.path.join(CRAWL_DIR, "segments")
        latest_segment = max([os.path.join(segments_dir, d) for d in os.listdir(segments_dir)], key=os.path.getmtime)
        #Fetch
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "fetch", latest_segment], check=True)
        #Parse
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "parse", latest_segment], check=True)
        #Update DB
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "updatedb", f"{CRAWL_DIR}/crawldb", latest_segment], check=True)
        print("Crawl Complete!")

if __name__ == '__main__':
    main()
