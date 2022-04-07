from xhtml2pdf import pisa
from string import Template


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
