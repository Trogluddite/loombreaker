#!/usr/bin/env python

import subprocess
import os

NUTCH_HOME = '/home/mpappas/apache-nutch-1.19'
CRAWL_DIR = '/home/mpappas/apache-nutch-1.19/runtime/local/crawl'
NUTCH_BIN = f'{NUTCH_HOME}/runtime/local/bin/nutch'
SEGMENTS_DIR = os.path.join(CRAWL_DIR, "segments")
SEED_FILE = '/home/mpappas/apache-nutch-1.19/runtime/local/urls/seed.txt'
NUM_ROUNDS = 1 #Need to eventually allow an argument

JAVA_HOME = '/usr/lib/jvm/default-java'

def main():

    local_env = os.environ.copy()
    local_env['JAVA_HOME'] = JAVA_HOME

    #Set first to true
    first = 1
    
    #Initialize Crawl
    subprocess.run([f"{NUTCH_BIN}", "inject", f"{CRAWL_DIR}/crawldb", SEED_FILE], env=local_env, check=True)
    
    #Run Crawler
    for i in range(1, NUM_ROUNDS + 1):
        print(f"Crawl Round: {i}")
 
    #Generate Fetch List. Tune generation if crawl has run more than once
        if first:
            subprocess.run([f"{NUTCH_BIN}", "generate", f"{CRAWL_DIR}/crawldb", f"{CRAWL_DIR}/segments"], env=local_env, check=True)
            first = 0
        else:
            subprocess.run([f"{NUTCH_BIN}", "generate", f"{CRAWL_DIR}/crawldb", f"{CRAWL_DIR}/segments", "-topN", "1000"], env=local_env, check=True)
    
        #Find latest segment
        raw_latest_segment = subprocess.run(f"ls -d {SEGMENTS_DIR}/2* | tail -1", shell=True, text=True, capture_output=True)
        latest_segment = raw_latest_segment.stdout.strip()
          
        while True: #A glitch was introduced when the process was stopped in the middle, and it required the half finished segments to be deleted. I added a command that removes the segment if the command cannot finished.
            try:
                #Fetch
                subprocess.run([f"{NUTCH_BIN}", "fetch", latest_segment], env=local_env, check=True)
        
                #Parse
                subprocess.run([f"{NUTCH_BIN}", "parse", latest_segment], env=local_env, check=True)

                #Update DB
                subprocess.run([f"{NUTCH_BIN}", "updatedb", f"{CRAWL_DIR}/crawldb", latest_segment], env=local_env, check=True)
                print("Crawl Complete!")
            except:
                subprocess.run(["rm", "-r", latest_segment])

    #Invert Links for Indexing
    subprocess.run([f"{NUTCH_BIN}", "invertlinks", f"{CRAWL_DIR}/linkdb", "-dir", f"{CRAWL_DIR}/segments"], env=local_env, check=True)
    
    #Index into Solr
    subprocess.run([f"{NUTCH_BIN}", "index", f"{CRAWL_DIR}/crawldb/", "-linkdb", f"{CRAWL_DIR}/linkdb/", f"{latest_segment}", "-filter", "-normalize", "-deleteGone"], env=local_env, check=True)


if __name__ == '__main__':
    main()
