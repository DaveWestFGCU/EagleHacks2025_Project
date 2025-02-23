from logging.handlers import QueueHandler, QueueListener
import queue

# Create a Queue object and a QueueHandler
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)

# Create a listener
listener = QueueListener(log_queue)