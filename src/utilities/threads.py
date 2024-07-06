from psutil import virtual_memory
import threading


MEM_USED_PER_INSTANCE_IN_MB: int = 500  # Closer to 250, but better safe than sorry
MEM_USED_PER_INSTANCE_IN_BYTES: int = MEM_USED_PER_INSTANCE_IN_MB * (1024 * 1024)  # Converts MB to Bytes for increased accuracy
AVAILABLE_SYS_MEM_IN_BYTES: int = virtual_memory().available

# Create a thread-local storage object
thread_local: threading.local = threading.local()
thread_lock: threading.Lock = threading.Lock()
thread_counter: int = 0


def calc_safe_threads() -> int:
    max_threads = calc_max_threads()
    return max((max_threads + 1) // 2, 1)


def calc_max_threads() -> int:
    try:
        max_threads = AVAILABLE_SYS_MEM_IN_BYTES // MEM_USED_PER_INSTANCE_IN_BYTES
        return max(max_threads, 1)
    except Exception:
        return 1


def get_thread_id() -> int:
    global thread_lock
    global thread_counter
    # This lock is required to ensure only one thread at a time attemps to increment the counter
    # This is techincally required to guarantee data race freedom
    with thread_lock:
        thread_counter += 1
        if not hasattr(thread_local, "id"):
            thread_local.id = thread_counter
    return thread_local.id
