import base64
from typing import Callable
from faker import Faker
from app.utils import generate_details_log, convert_html_to_pdf
import psutil
import shutil
import concurrent.futures
import multiprocessing

from datetime import datetime, timedelta

fake = Faker()


def job(i: int) -> None:
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

    def __init__(self) -> None:

        self.start = datetime.now()
        self.phase_2_sub_duration = []
        self.phase_2_details = []

        return super().__init__()

    def __worker(self, i):
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

    def common_cv_generate(self, no_of_cv):
        for i in range(0, no_of_cv):
            self.__worker(i)

    def multhreading_cv_generate(self, no_of_cv, max_workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, no_of_cv):
                executor.submit(self.__worker, i)

    def multiprocessing_cv_generate(self, no_of_cv, max_workers):

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
        shutil.make_archive("zipped_cvs", "zip", "results")

    def get_avg_time(self):
        return sum(self.phase_2_sub_duration, timedelta()) / len(self.phase_2_sub_duration)

    def get_duration(self):
        end = datetime.now()
        return end - self.start

    def get_details(self):
        return self.phase_2_details
