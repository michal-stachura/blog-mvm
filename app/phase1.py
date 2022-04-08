import multiprocessing
import requests
import shutil
import psutil
import concurrent.futures

from datetime import datetime, timedelta
from app.utils import generate_details_log


def multiprocessing_worker(i, url, phase_1_sub_duration, phase_1_details, generate_details_log):
    subprocess_start = datetime.now()
    phase_1_details.append(
        generate_details_log(
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
        generate_details_log(
            i,
            psutil.pids(),
            psutil.cpu_percent(interval=None),
            psutil.virtual_memory()
        )
    )


class PhaseOne():

    def __init__(self) -> None:

        self.start = datetime.now()
        self.phase_1_sub_duration = []
        self.phase_1_details = []
        self.url = "https://thispersondoesnotexist.com/image"
        return super().__init__()

    def __worker(self, i):
        subprocess_start = datetime.now()
        self.phase_1_details.append(
            generate_details_log(
                i,
                psutil.pids(),
                psutil.cpu_percent(interval=None),
                psutil.virtual_memory(),
                subprocess_start
            )
        )

        res = requests.get(self.url, stream=True)
        image_name = f"img{i}.jpg"
        if res.status_code == 200:
            res.raw.decode_content = True
            with open(f"downloads/{image_name}", "wb") as file:
                shutil.copyfileobj(res.raw, file)

        subprocess_end = datetime.now()
        self.phase_1_sub_duration.append(subprocess_end - subprocess_start)
        self.phase_1_details.append(
            generate_details_log(
                i,
                psutil.pids(),
                psutil.cpu_percent(interval=None),
                psutil.virtual_memory()
            )
        )

    def common_images_download(self, no_of_images) -> None:
        for i in range(0, no_of_images):
            self.__worker(i)

    def multhreading_images_download(self, no_of_images, max_workers=10) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, no_of_images):
                executor.submit(self.__worker, i)

    def multprocessing_images_download(self, no_of_images, max_workers=10):

        with multiprocessing.Manager() as manager:
            phase_1_sub_duration = manager.list()  # Can be shared between processes
            phase_1_details = manager.list()  # Can be shared between processes

            pool = multiprocessing.Pool(max_workers)
            for i in range(0, no_of_images):
                pool.apply_async(multiprocessing_worker, args=(
                    i, self.url, phase_1_sub_duration, phase_1_details, generate_details_log))

            pool.close()
            pool.join()

            self.phase_1_sub_duration = list(phase_1_sub_duration)
            self.phase_1_details = list(phase_1_details)

    def get_avg_time(self):
        return sum(self.phase_1_sub_duration, timedelta()) / len(self.phase_1_sub_duration)

    def get_duration(self):
        end = datetime.now()
        return end - self.start

    def get_details(self):
        return self.phase_1_details
