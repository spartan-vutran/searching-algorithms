import threading
import ctypes
import time


def afunction(timeout, result, event):
  time.sleep(timeout)
  print("Hello I am executed")
  result.append("Hello")
  event.set()
  return 

class thread_with_exception(threading.Thread):
    def __init__(self, name, target, args):
      threading.Thread.__init__(self, target=target, args = args)
      self.name = name
          
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

hello = ["yeye"]
event = threading.Event()
timeout = 2
start_time = time.time()
t1 = thread_with_exception('Thread 1', target=afunction, args = (2.1, hello, event) )
t1.start()

while not event.is_set():
  t1.join(timeout=0.1)
  print(f"Time executed {time.time() - start_time}")
  if time.time() - start_time > timeout:
    event.set()
    t1.raise_exception()
    t1.join()
    print("Thread timeout, continue to execute")

print(hello)