import multiprocessing
import requests
import shutil
import psutil
import concurrent.futures

from datetime import datetime, timedelta
from app.utils import Report

phase_1_details = []
phase_1_sub_duration = []
url = "https://thispersondoesnotexist.com/image"


def generate_details(task, pids, cpu, memory, start=None):
    task_start_or_end = "start" if start != None else "end"

    return f"Task: {task} ({task_start_or_end}) - PID: {len(pids)} CPU: {cpu}%, RAM (GB): avl: {round(memory.available/1073741824, 2)}, used: {round(memory.used/1073741824, 2)}, {memory.percent}%)"


def worker(i):
    subprocess_start = datetime.now()
    phase_1_details.append(
        generate_details(
            i,
            psutil.pids(),
            psutil.cpu_percent(interval=None),
            psutil.virtual_memory(),
            subprocess_start
        )
    )

    res = requests.get(url, stream=True)
    image_name = f"img{i}.jpg"
    if res.status_code == 200:
        res.raw.decode_content = True
        with open(f"downloads/{image_name}", "wb") as file:
            shutil.copyfileobj(res.raw, file)

    subprocess_end = datetime.now()
    phase_1_sub_duration.append(subprocess_end - subprocess_start)
    phase_1_details.append(
        generate_details(
            i,
            psutil.pids(),
            psutil.cpu_percent(interval=None),
            psutil.virtual_memory()
        )
    )


class PhaseOne(Report):
    phase_1_sub_duration = []
    phase_1_details = []
    url = "https://thispersondoesnotexist.com/image"
    start = None

    def __init__(self) -> None:

        self.start = datetime.now()
        return super().__init__()

    # def __worker(self, i):
    #     subprocess_start = datetime.now()
    #     self.phase_1_details.append(
    #         self.generate_details(
    #             i,
    #             psutil.pids(),
    #             psutil.cpu_percent(interval=None),
    #             psutil.virtual_memory(),
    #             subprocess_start
    #         )
    #     )

    #     res = requests.get(self.url, stream=True)
    #     image_name = f"img{i}.jpg"
    #     if res.status_code == 200:
    #         res.raw.decode_content = True
    #         with open(f"downloads/{image_name}", "wb") as file:
    #             shutil.copyfileobj(res.raw, file)

    #     subprocess_end = datetime.now()
    #     self.phase_1_sub_duration.append(
    #         self.get_time_diff(subprocess_start, subprocess_end))
    #     self.phase_1_details.append(
    #         self.generate_details(
    #             i,
    #             psutil.pids(),
    #             psutil.cpu_percent(interval=None),
    #             psutil.virtual_memory()
    #         )
    #     )

    def common_images_download(self, no_of_images) -> None:
        for i in range(0, no_of_images):
            worker(i)

    def multhreading_images_download(self, no_of_images, max_workers=10) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, no_of_images):
                executor.submit(worker, i)

    def multprocessing_images_download(self, no_of_images, max_workers=10):

        global worker

        def worker(i, phase_1_sub_duration, phase_1_details):
            # subprocess_start = datetime.now()
            phase_1_details.append(
                f"Task: {i} (start) - PID: {len(psutil.pids())} CPU: {psutil.cpu_percent(interval=None)}%, RAM (GB): avl: {round(psutil.virtual_memory().available/1073741824, 2)}, used: {round(psutil.virtual_memory().used/1073741824, 2)}, {psutil.virtual_memory().percent}%)"
            )

            res = requests.get(
                "https://thispersondoesnotexist.com/image", stream=True)
            image_name = f"img{i}.jpg"
            if res.status_code == 200:
                res.raw.decode_content = True
                with open(f"downloads/{image_name}", "wb") as file:
                    shutil.copyfileobj(res.raw, file)

            subprocess_end = datetime.now()
            phase_1_sub_duration.append(subprocess_end - subprocess_start)
            phase_1_details.append(
                f"Task: {i} (end) - PID: {len(psutil.pids())} CPU: {psutil.cpu_percent(interval=None)}%, RAM (GB): avl: {round(psutil.virtual_memory().available/1073741824, 2)}, used: {round(psutil.virtual_memory().used/1073741824, 2)}, {psutil.virtual_memory().percent}%)")

        with multiprocessing.Manager() as manager:
            phase_1_sub_duration = manager.list()  # Can be shared between processes
            phase_1_details = manager.list()  # Can be shared between processes

            pool = multiprocessing.Pool(max_workers)
            for i in range(0, no_of_images):
                pool.apply_async(worker, args=(
                    i, phase_1_sub_duration, phase_1_details))

            pool.close()
            pool.join()

            self.phase_1_sub_duration = list(phase_1_sub_duration)
            self.phase_1_details = list(phase_1_details)

    def get_avg_time(self):
        return sum(phase_1_sub_duration, timedelta()) / len(phase_1_sub_duration)

    def get_duration(self):
        end = datetime.now()
        return end - self.start

    def get_details(self):
        return phase_1_details
