#encoding=UTF8
#code by LP
#2013-8-27

'''
线程池
'''

from Queue import Queue
from threading import Thread
import traceback

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks, daemon):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = daemon
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: func(*args, **kargs)
            except: print traceback.print_exc()
            self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads, daemon=True):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks, daemon)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

    def get_task_num(self):
        return self.tasks.qsize()
