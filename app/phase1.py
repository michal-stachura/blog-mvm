import multiprocessing
from typing import Callable
import requests
import shutil
import psutil
import concurrent.futures

from datetime import datetime, timedelta
from app.utils import generate_details_log


def job(i: int, url: str) -> None:
    """
    Phase 1 job
    Getting random face images from https://thispersondoesnotexist.com/image
    and save it as separate files

    Args:
        i (int): Task ID
        url (str): Random face generator url
    """
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
    """
    Multiprocessing worker.
    Must be global due to: https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled

    Args:
        i (int): Task ID
        url (str): Random face generator url
        phase_1_sub_duration (Callable): Manager task duration log list
        phase_1_details (Callable): Manager task details log list
        job (Callable[[int, str], None]): Executable function to do by worker
        generate_details_log (_type_): Executable function to generate logs
    """
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
    """
    Phase 1 class
    """

    def __init__(self) -> None:

        self.start = datetime.now()
        self.phase_1_sub_duration = []
        self.phase_1_details = []
        self.url = "https://thispersondoesnotexist.com/image"
        return super().__init__()

    def __worker(self, i: int) -> None:
        """
        Phase 1 worker

        Args:
            i (int): Task ID
        """
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
        """
        Gathering random faces images method
        Oridinary loop

        Args:
            no_of_images (int): Number of images to be downloaded (Number of CV's)
        """
        for i in range(0, no_of_images):
            self.__worker(i)

    def multhreading_images_download(self, no_of_images: int, max_workers: int = 10) -> None:
        """
        Gathering random faces images method
        Multithreading approach

        Args:
            no_of_images (int): Number of images to be downloaded (Number of CV's)
            max_workers (int, optional): Number of parallel threads. Defaults to 10.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, no_of_images):
                executor.submit(self.__worker, i)

    def multprocessing_images_download(self, no_of_images: int, max_workers: int = 10) -> None:
        """
        Gathering random faces images method
        Multiprocessing approach

        Args:
            no_of_images (int): Number of images to be downloaded (Number of CV's)
            max_workers (int, optional): Number of parallel processes. Defaults to 10.
        """
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
        """
        Calculate average time for Phase 1

        Returns:
            datetime: Datetime object with average Task execution time
        """
        return sum(self.phase_1_sub_duration, timedelta()) / len(self.phase_1_sub_duration)

    def get_duration(self) -> datetime:
        """
        Calculate Phase 1 duration

        Returns:
            datetime: Datetime object with Phase 1 duration
        """
        end = datetime.now()
        return end - self.start

    def get_details(self) -> list:
        """
        Returns:
            list: Phase 1 detailed report
        """
        return self.phase_1_details
