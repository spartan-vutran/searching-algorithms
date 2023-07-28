
from PIL import Image, ImageTk
import heapq
import threading
import ctypes

def resize_icon_image(image_path, width, height):
    # Open the image using PIL
    image = Image.open(image_path)
    # Resize the image to fit the button size
    resized_image = image.resize((width, height), Image.LANCZOS)
    # Create a PhotoImage object from the resized image
    return ImageTk.PhotoImage(resized_image)


def nullHeuristic(state, problem=None):
  return 0

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



class Stack:
    "A container with a last-in-first-out (LIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0
    
class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
      entry = (priority, self.count, item)
      heapq.heappush(self.heap, entry)
      self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
      # If item already in priority queue with higher priority, update its priority and rebuild the heap.
      # If item already in priority queue with equal or lower priority, do nothing.
      # If item not in priority queue, do the same thing as self.push.
      flag = False
      for index, (p, c, i) in enumerate(self.heap):
        if i[0] == item[0]: #Compare object
          flag = True
          if p <= priority:
              break
          del self.heap[index]
          self.heap.append((priority, c, item))
          heapq.heapify(self.heap)
          break
      if not flag:
        self.push(item, priority)


