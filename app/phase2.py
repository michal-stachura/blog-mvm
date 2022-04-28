import base64
from typing import Callable
from faker import Faker
from app.utils import generate_details_log, convert_html_to_pdf
import psutil
import shutil
import concurrent.futures
import multiprocessing

from datetime import date, datetime, timedelta

fake = Faker()


def job(i: int) -> None:
    """
    Phase 2 job
    Generate PDF file with random employee data

    Args:
        i (int): Task ID
    """
    with open(f"downloads/img{i}.jpg", "rb") as img:
        face = base64.b64encode(img.read())
    context = {
        "name": fake.name(),
        "birth": fake.date(),
        "phone": fake.phone_number(),
        "email": fake.email(),
        "address": fake.address(),
        "bio": fake.text(),
        "face": f"data:image/jpeg;base64,{face.decode('utf-8')}"
    }

    output_filename = f"test{i}.pdf"
    convert_html_to_pdf(context, output_filename)


def multiprocessing_worker(
    i: int,
    phase_2_sub_duration: Callable,
    phase_2_details: Callable,
    job: Callable[[int, str], None],
    generate_details_log: Callable[[int, list, float, Callable, datetime | None], str],
    fake: Callable
) -> None:
    """
    Multiprocessing worker.
    # what-can-be-pickled-and-unpickled
    Must be global due to: https://docs.python.org/3/library/pickle.html

    Args:
        i (int): Task ID
        phase_2_sub_duration (Callable): Manager task duration log list
        phase_2_details (Callable): Manager task tetails log list
        job (Callable[[int, str], None]): Executable function to do by worker
        generate_details_log (Callable[[int, list, float, Callable, datetime  |  None], str]): Executable function to generate logs
        fake (Callable): function used to generate random fake employee data
    """
    fake = fake
    subprocess_start = datetime.now()
    phase_2_details.append(
        generate_details_log(
            i,
            psutil.pids(),
            psutil.cpu_percent(interval=None),
            psutil.virtual_memory(),
            subprocess_start
        )
    )

    job(i=i)

    subprocess_end = datetime.now()
    phase_2_sub_duration.append(subprocess_end - subprocess_start)
    phase_2_details.append(
        generate_details_log(
            i,
            psutil.pids(),
            psutil.cpu_percent(interval=None),
            psutil.virtual_memory()
        )
    )


class PhaseTwo():
    """
    Phase 2 class
    """

    def __init__(self) -> None:

        self.start = datetime.now()
        self.phase_2_sub_duration = []
        self.phase_2_details = []

        return super().__init__()

    def __worker(self, i) -> None:
        """
        Phase 2 worker

        Args:
            i (_type_): Task ID
        """
        subprocess_start = datetime.now()
        self.phase_2_details.append(
            generate_details_log(
                i,
                psutil.pids(),
                psutil.cpu_percent(interval=None),
                psutil.virtual_memory(),
                subprocess_start
            )
        )

        job(i)

        subprocess_end = datetime.now()
        self.phase_2_sub_duration.append(subprocess_end - subprocess_start)
        self.phase_2_details.append(
            generate_details_log(
                i,
                psutil.pids(),
                psutil.cpu_percent(interval=None),
                psutil.virtual_memory()
            )
        )

    def common_cv_generate(self, no_of_cv) -> None:
        """
        Generate CV PDF files
        Oridinary loop

        Args:
            no_of_cv (_type_): Number of files to be generated (Number of CV's)
        """
        for i in range(0, no_of_cv):
            self.__worker(i)

    def multhreading_cv_generate(self, no_of_cv, max_workers: int = 10) -> None:
        """
        Generate CV PDF files
        Multithreading approach

        Args:
            no_of_cv (_type_): Number of files to be generated (Number of CV's)
            max_workers (_type_): max_workers (int, optional): Number of parallel threads. Defaults to 10.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, no_of_cv):
                executor.submit(self.__worker, i)

    def multiprocessing_cv_generate(self, no_of_cv, max_workers: int = 10) -> None:
        """
        Generate CV PDF files
        Multithreading approach

        Args:
            no_of_cv (_type_): Number of files to be generated (Number of CV's)
            max_workers (_type_): max_workers (int, optional): Number of parallel processes. Defaults to 10.
        """

        with multiprocessing.Manager() as manager:
            phase_2_sub_duration = manager.list()  # Can be shared between processes
            phase_2_details = manager.list()  # Can be shared between processes

            pool = multiprocessing.Pool(max_workers)
            for i in range(0, no_of_cv):
                pool.apply_async(multiprocessing_worker, args=(
                    i, phase_2_sub_duration, phase_2_details, job, generate_details_log, fake))

            pool.close()
            pool.join()

            self.phase_2_sub_duration = list(phase_2_sub_duration)
            self.phase_2_details = list(phase_2_details)

    def zip_cvs(self):
        """
        Creates generated files ZIP file method
        """
        shutil.make_archive("zipped_cvs", "zip", "results")

    def get_avg_time(self) -> datetime:
        """
        Calculate average time for Phase 2

        Returns:
            datetime: Datetime object with average Task execution time
        """
        return sum(self.phase_2_sub_duration, timedelta()) / len(self.phase_2_sub_duration)

    def get_duration(self) -> datetime:
        """
        Calculate Phase 2 duration

        Returns:
            datetime: Datetime object with Phase 2 duration
        """
        end = datetime.now()
        return end - self.start

    def get_details(self) -> list:
        """
        Returns:
            list: Phase 2 detailed report
        """
        return self.phase_2_details
