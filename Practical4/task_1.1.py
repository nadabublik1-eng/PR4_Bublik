import threading
import time


def download_simulation(file_name: str, size_mb: float) -> dict:
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Початок завантаження '{file_name}' ({size_mb} MB)...")

    time.sleep(size_mb * 0.5)

    return {"file": file_name, "size": size_mb, "thread": thread_name}


class MonitorThread(threading.Thread):
    def __init__(self, interval: float = 1.0):
        super().__init__(name="Monitor", daemon=True)
        self.interval = interval
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            print(f"[Monitor] Активних потоків: {threading.active_count()}")
            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()


def main():
    files = [
        ("data.csv", 2.5),
        ("report.pdf", 1.0),
        ("image.png", 0.5),
        ("archive.zip", 4.0),
        ("log.txt", 0.3),
    ]

    monitor = MonitorThread(interval=0.5)
    monitor.start()

    threads = [
        threading.Thread(
            target=download_simulation,
            args=(file_name, size_mb),
            name=f"Download-{i}"
        )
        for i, (file_name, size_mb) in enumerate(files, 1)
    ]

    start = time.perf_counter()

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start

    monitor.stop()
    monitor.join()

    print(f"\nУсі файли завантажено за {elapsed:.2f} сек")

    sequential_start = time.perf_counter()

    for file_name, size_mb in files:
        download_simulation(file_name, size_mb)

    sequential_time = time.perf_counter() - sequential_start

    print(f"\nПослідовне виконання: {sequential_time:.2f} сек")
    print(f"Паралельне виконання: {elapsed:.2f} сек")
    print(f"Прискорення: {sequential_time / elapsed:.2f}x")


if __name__ == "__main__":
    main()