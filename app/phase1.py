import multiprocessing
from typing import Callable
import requests
import shutil
import psutil
import concurrent.futures

from datetime import datetime, timedelta
from app.utils import generate_details_log


def job(i: int, url: str) -> None:
    res = requests.get(url, stream=True)
    image_name = f"img{i}.jpg"
    if res.status_code == 200:
        res.raw.decode_content = True
        with open(f"downloads/{image_name}", "wb") as file:
            shutil.copyfileobj(res.raw, file)


def multiprocessing_worker(
    i: int,
    url: str,
    phase_1_sub_duration: Callable,
    phase_1_details: Callable,
    job: Callable[[int, str], None],
    generate_details_log
) -> None:
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

    job(i=i, url=url)

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

    def __worker(self, i: int) -> None:
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

        job(i=i, url=self.url)

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

    def common_images_download(self, no_of_images: int) -> None:
        for i in range(0, no_of_images):
            self.__worker(i)

    def multhreading_images_download(self, no_of_images: int, max_workers: int = 10) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, no_of_images):
                executor.submit(self.__worker, i)

    def multprocessing_images_download(self, no_of_images: int, max_workers: int = 10) -> None:

        with multiprocessing.Manager() as manager:
            phase_1_sub_duration = manager.list()  # Can be shared between processes
            phase_1_details = manager.list()  # Can be shared between processes

            pool = multiprocessing.Pool(max_workers)
            for i in range(0, no_of_images):
                pool.apply_async(multiprocessing_worker, args=(
                    i, self.url, phase_1_sub_duration, phase_1_details, job, generate_details_log))

            pool.close()
            pool.join()

            self.phase_1_sub_duration = list(phase_1_sub_duration)
            self.phase_1_details = list(phase_1_details)

    def get_avg_time(self) -> datetime:
        return sum(self.phase_1_sub_duration, timedelta()) / len(self.phase_1_sub_duration)

    def get_duration(self) -> datetime:
        end = datetime.now()
        return end - self.start

    def get_details(self) -> list:
        return self.phase_1_details
