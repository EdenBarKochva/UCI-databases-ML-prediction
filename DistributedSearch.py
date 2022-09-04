import re
import threading



findmin = []  # the threads will send the result to her
index = {}   # the threads will send the result to her



class myThread(threading.Thread):    # calss for threads
    def __init__(self, ThreadID, txt, pattern, duplic, end1):
        threading.Thread.__init__(self)
        self.threadID = ThreadID        # ID
        self.txt = txt                  # txt to search through
        self.pattern = pattern
        self.duplic = duplic
        self.end1 = end1

    def run(self):
        if self.duplic != -1:
            if self.threadID == 1:
                for match in re.finditer(self.pattern, self.txt):
                    findmin.append((match.start()))
                    break
            else:
                for match in re.finditer(self.pattern, self.txt):
                    findmin.append((match.start()) + ((self.threadID - 1) * self.end1) - self.duplic)  # calculate the original index
                    break
        if self.duplic == -1:
            for i in range(len(self.pattern)):
                for match in re.finditer(self.pattern[i], self.txt):
                    if self.pattern[i] not in index.keys():
                        index[self.pattern[i]] = [(match.start()) + ((self.threadID - 1) * self.end1)]  # calculate the original index
                    else:
                        index[self.pattern[i]].append((match.start()) + ((self.threadID - 1) * self.end1))


def DistributedSearch(textfile, StringToSearch, nThreads, Delta):
    if nThreads == 0:    # we must have at least one thread
        return "you always have 1 thread"
    with open(textfile, encoding="utf8") as f:
        read = f.read()
    read = read.replace("\n", "")
    lenn = len(read)
    txt = []
    threads = []
    threadID = 1   # threadID
    start = 0
    end = lenn // nThreads
    modulo1 = lenn % nThreads   # will add to the last thread
    end1 = end
    if Delta != -1:
        pattern = make_regex(StringToSearch,Delta)
        duplic = (((len(StringToSearch) - 1) * (Delta)) + len(StringToSearch) - 1)
        for i in range(nThreads-1):    # split the text for each thread
            txt.append(read[start : end])
            start = end - duplic
            end = end + end1
        txt.append(read[start : end + modulo1])

        for i in range(nThreads):     # create nThreads threads
            thread = myThread(threadID, txt[i], pattern, duplic, end1)
            thread.start()
            threads.append(thread)
            threadID += 1

        for i in threads:   # create nThreads threads
            i.join()

        if len(findmin) > 0:
            l = min(findmin)
            findmin.clear()   # clear the list for the next test
            return l
        else:
            return "not found."



    if Delta == -1:
        start = 0
        end = int(lenn / nThreads)
        end1 = end
        result = [float('inf')]
        result = result*len(StringToSearch)
        for i in range(nThreads-1):   # split the text for each thread
            txt.append(read[start : end])
            start = end1 + start
            end = end + end1
        txt.append(read[start: end + modulo1])

        for i in range(nThreads):   # create nThreads threads
            thread = myThread(threadID, txt[i], StringToSearch, -1, end1)
            thread.start()
            threads.append(thread)
            threadID += 1
        for i in threads:   # we will wait until all threads to end
            i.join()

        for i in range(len(StringToSearch)):
            if StringToSearch[i] not in index.keys():
                return "not found."
            else:
                for j in index[StringToSearch[i]]:
                    if i == 0:
                        result[0] = min(index[StringToSearch[0]])
                        break
                    if j > result[i-1] and j < result[i]:
                        result[i] = j
                        break
                else:
                    return "not found."
        index.clear()  # clear the dictionary for the next test
        return result


def make_regex(StringToSearch, Delta):    # creating the regex
    regex = ""
    string_search = list(StringToSearch)
    all = ["[\w|\W]"]
    for i in range(len(StringToSearch)-1):
        letters = f"{string_search[i]+all[0]}{{{Delta}}}"
        regex = regex + letters
    regex = regex + string_search[-1]
    return regex


if __name__ == "__main__":
    import sys
    print(DistributedSearch(sys.argv[1], sys.argv[2], int(sys.argv[3]),int(sys.argv[4])))




