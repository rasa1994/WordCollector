from collections import deque
from enum import unique
from inspect import stack
from os import times
from urllib import request
import requests, bs4, re
import time
import threading

lock = threading.Lock()

def has_cyrillic(text):
    for char in text:
        if not re.search('[а-шА-Ш]', char):
            return False
    return True

def hasHttps(text):
    if text == None:
        return False
    else:
        return """https://sr""" in text

webPageToVisit = 100
startingUrl = str("https://sr.wikipedia.org/wiki/%D0%A1%D1%80%D0%B1%D0%B8%D1%98%D0%B0")
stackUrls = deque()
stackUrls.append(startingUrl)
file = open("Cyrilic.txt","a",encoding="utf-16")
unique_words = set()

def WorkerMethod(event):
    global webPageToVisit, stackUrls, unique_words, allLinks, lock
    while len(unique_words) < 500000 : #creating dictionary of 500000 words
        if len(stackUrls) == 0:
            event.wait()

        lock.acquire(blocking=True)
        startingUrl = stackUrls.popleft()
        lock.release()
        res = requests.get(startingUrl)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        listWords = soup.text.split()
        for word in listWords:
            if has_cyrillic(word):
                lock.acquire(blocking=True)
                unique_words.add(word)
                lock.release()
    
        allLinks = soup.find_all("a")
        for links in allLinks:
            link = links.get("href")
            if hasHttps(link) and len(stackUrls) <= 1000:
                lock.acquire(blocking=True)
                stackUrls.append(link)
                lock.release()
                event.set()
    

timeStart = time.perf_counter()
threads = []
number_of_threads = 10
event = threading.Event()
for _ in range(number_of_threads):
    t = threading.Thread(target = WorkerMethod, args = [event])
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

wordsToList = list(unique_words)
wordsToList.sort()
for word in wordsToList:
    file.write(word)
    file.write("\n")
file.close()
timeEnd = time.perf_counter()

print(f"finished for {round(timeEnd - timeStart, 2)}")
