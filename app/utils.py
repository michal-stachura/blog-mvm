from datetime import datetime
from typing import Callable
from xhtml2pdf import pisa
from string import Template


def generate_details_log(
    task: int,
    pids: list,
    cpu: float,
    memory: Callable,
    start: datetime | None = None
) -> str:

    task_start_or_end = "start" if start != None else "end"

    return f"Task: {task} ({task_start_or_end}) - PID: {len(pids)} CPU: {cpu}%, RAM (GB): avl: {round(memory.available/1073741824, 2)}, used: {round(memory.used/1073741824, 2)}, {memory.percent}%)"


def convert_html_to_pdf(context, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(f"results/{output_filename}", "w+b")

    with open("template/pdf_template.html", "r") as pdf:
        src = Template(pdf.read())
        result = src.substitute(context)

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        result,                # the HTML to convert
        dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return False on success and True on errors
    return pisa_status.err
