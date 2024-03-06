import requests as http
import logging as log
from multiprocessing import Process, Queue

urls = [
  'http://www.python.org',
  'https://docs.python.org/3/',
  'https://docs.python.org/3/whatsnew/3.7.html',
  'https://docs.python.org/3/tutorial/index.html',
  'https://docs.python.org/3/library/index.html',
  'https://docs.python.org/3/reference/index.html',
  'https://docs.python.org/3/using/index.html',
  'https://docs.python.org/3/howto/index.html',
  'https://docs.python.org/3/installing/index2.html',
  'https://docs.python.org/3/distributing/index2.html',
  'https://docs.python.org/3/extending/index2.html',
  'https://docs.python.org/3/c-api/index2.html',
  'https://docs.python.org/3/faq/index2.html'
  ]

log.basicConfig(level=log.INFO, format="%(asctime)s %(levelname)s [%(processName)s:%(threadName)s] - %(message)s")

class UrlCheckingTask:

    def __init__(self, urls):
        self.urls = urls        
        self.result = Queue()
        self.process = Process(target = self.check_urls)

    def start(self):
        self.process.start()
    
    def close(self):
        self.process.join()
    
    def get(self):
        return self.result.get()
    
    def check_urls(self):
        result = {}
        for url in self.urls:
            result[url] = self.__check_url(url)        
        self.result.put(result)

    def __check_url(self, url):
        try:
            result = http.get(url, timeout=2)
            if result.ok:
                log.info(f"Result of of checking url={url} is ok")
            else:
                log.warning(f"Result of of checking url={url} is failed")
            return result.ok
        except Exception as error:
            log.error(f"Error of checking url={url}: {error}")
            return False



if __name__ == "__main__":
    count_processes = 5
    tasks = []
    try:
        # split all urls on chunks
        chunks = [[] for i in range(count_processes)]
        for i in range(len(urls)):
            chunks[i % count_processes].append(urls[i])
        
        # run every chunk in sub-process
        for chunk in chunks:
            if len(chunk) > 0:
                task = UrlCheckingTask(chunk)
                tasks.append(task)
                task.start()

        # wait and agregate results
        results = {}
        for task in tasks:
           results = dict(**results, **task.get())
        # printing results
        checks_list= ""
        for url, result in results.items():
            checks_list += f"\n\t{url} - is {'ok' if result else 'failed'}"
        log.info(f"Results:{checks_list}")
    finally:
        for task in tasks:
            task.close()