from logging.handlers import QueueHandler, QueueListener
import logging, queue, os

# Create a Queue object and a QueueHandler
log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)

# Create a listener
listener = QueueListener(log_queue)


def create_logger(job_id) -> logging.Logger:
    try:
        job_logger = logging.getLogger(job_id)
        job_logger.setLevel(logging.DEBUG)
        job_logger.addHandler(queue_handler)

    except Exception as e:
        raise

    return job_logger


def create_handler(job_id) -> logging.Handler:
    try:
        file_handler = logging.FileHandler(filename=os.path.join('jobs', job_id, 'job_log.txt'))
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        file_handler.addFilter(logging.Filter(name=job_id))

        # Add to listener's handlers
        handlers = list(listener.handlers)
        handlers.append(file_handler)
        listener.handlers = tuple(handlers)

    except Exception as e:
        raise

    return file_handler


def remove_queue_handler(handler) -> None:
    try:
        handlers = list(listener.handlers)
        handlers.remove(handler)
        listener.handlers = tuple(handlers)
        handler.close()

    except Exception as e:
        print(f"ERROR REMOVING QUEUE HANDLER: {e}")