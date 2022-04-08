import base64
from faker import Faker
from app.utils import generate_details_log
import psutil
import concurrent.futures
import multiprocessing

from datetime import datetime, timedelta
from app.generate_pdf import convert_html_to_pdf

fake = Faker()


def job(i: int):
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


class PhaseTwo():

    phase_2_sub_duration = []
    phase_2_details = []
    fake = Faker()
    start = datetime.now()

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
        global worker

        def worker(i, phase_2_sub_duration, phase_2_details):
            subprocess_start = datetime.now()
            phase_2_details.append(
                f"Task: {i} (start) - PID: {len(psutil.pids())} CPU: {psutil.cpu_percent(interval=None)}%, RAM (GB): avl: {round(psutil.virtual_memory().available/1073741824, 2)}, used: {round(psutil.virtual_memory().used/1073741824, 2)}, {psutil.virtual_memory().percent}%)"
            )

            with open(f"downloads/img{i}.jpg", "rb") as img:
                face = base64.b64encode(img.read())
            context = {
                "name": self.fake.name(),
                "birth": self.fake.date(),
                "phone": self.fake.phone_number(),
                "email": self.fake.email(),
                "address": self.fake.address(),
                "bio": self.fake.text(),
                "face": f"data:image/jpeg;base64,{face.decode('utf-8')}"
            }

            output_filename = f"test{i}.pdf"
            convert_html_to_pdf(context, output_filename)

            subprocess_end = datetime.now()
            phase_2_sub_duration.append(subprocess_end - subprocess_start)
            phase_2_details.append(
                f"Task: {i} (end) - PID: {len(psutil.pids())} CPU: {psutil.cpu_percent(interval=None)}%, RAM (GB): avl: {round(psutil.virtual_memory().available/1073741824, 2)}, used: {round(psutil.virtual_memory().used/1073741824, 2)}, {psutil.virtual_memory().percent}%)")

        with multiprocessing.Manager() as manager:
            phase_2_sub_duration = manager.list()  # Can be shared between processes
            phase_2_details = manager.list()  # Can be shared between processes

            pool = multiprocessing.Pool(max_workers)
            for i in range(0, no_of_cv):
                pool.apply_async(worker, args=(
                    i, phase_2_sub_duration, phase_2_details))

            pool.close()
            pool.join()

            self.phase_2_sub_duration = list(phase_2_sub_duration)
            self.phase_2_details = list(phase_2_details)

    def get_avg_time(self):
        return sum(self.phase_2_sub_duration, timedelta()) / len(self.phase_2_sub_duration)

    def get_duration(self):
        end = datetime.now()
        return end - self.start

    def get_details(self):
        return self.phase_2_details
