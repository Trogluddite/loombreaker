import subprocess
import os

NUTCH_HOME = '/home/mpappas/apache-nutch-1.19'
CRAWL_DIR = '/home/mpappas/apache-nutch-1.19/crawl'
SEGMENTS_DIR = os.path.join(CRAWL_DIR, "segments")
SEED_FILE = '/home/mpappas/apache-nutch-1.19/urls/seed.txt'
NUM_ROUNDS = 1 #Need to eventually allow an argument

def main():

    #Set first to true
    first = 1
    
    #Initialize Crawl
    subprocess.run([f"{NUTCH_HOME}/bin/nutch", "inject", f"{CRAWL_DIR}/crawldb", SEED_FILE], check=True)
    
    #Run Crawler
    for i in range(1, NUM_ROUNDS + 1):
        print(f"Crawl Round: {i}")
 
        #Generate Fetch List. Tune generation if crawl has run more than once
        if first:
            subprocess.run([f"{NUTCH_HOME}/bin/nutch", "generate", f"{CRAWL_DIR}/crawldb", f"{CRAWL_DIR}/segments"], check=True)
            first = 0
        else:
            subprocess.run([f"{NUTCH_HOME}/bin/nutch", "generate", f"{CRAWL_DIR}/crawldb", f"{CRAWL_DIR}/segments", "-topN", "1000"], check=True)
   
        #Find latest segment
        raw_latest_segment = subprocess.run(f"ls -d {SEGMENTS_DIR}/2* | tail -1", shell=True, text=True, capture_output=True)
        latest_segment = raw_latest_segment.stdout.strip()
          
        #Fetch
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "fetch", latest_segment], check=True)
        
        #Parse
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "parse", latest_segment], check=True)
        
        #Update DB
        subprocess.run([f"{NUTCH_HOME}/bin/nutch", "updatedb", f"{CRAWL_DIR}/crawldb", latest_segment], check=True)
        print("Crawl Complete!")

    #Invert Links for Indexing
    subprocess.run([f"{NUTCH_HOME}/bin/nutch", "invertlinks", f"{CRAWL_DIR}/linkdb", "-dir", f"{CRAWL_DIR}/segments"], check=True)
    
    #Index into Solr
    subprocess.run([f"{NUTCH_HOME}/bin/nutch", "index", f"{CRAWL_DIR}/crawldb/", "-linkdb", f"{CRAWL_DIR}/linkdb/", f"{latest_segment}", "-filter", "-normalize", "-deleteGone"], check=True)


if __name__ == '__main__':
    main()
