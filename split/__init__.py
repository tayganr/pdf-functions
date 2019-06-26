import json
import io
import logging
from azure.storage.blob import BlockBlobService
import azure.functions as func
from PyPDF2 import PdfFileWriter, PdfFileReader

def main(req: func.HttpRequest) -> func.HttpResponse:

    # 1. Get Header Values
    account_name = req.headers.get('account_name')
    account_key = req.headers.get('account_key')
    input_container = req.headers.get('input_container')
    output_container = req.headers.get('output_container')
    blob_name = req.headers.get('blob_name')

    if None not in [account_name, account_key, input_container, output_container, blob_name]:

        # 2. Get PDF from Azure Blob Storage
        block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
        stream = io.BytesIO()   
        block_blob_service.get_blob_to_stream(container_name=input_container, blob_name=blob_name, stream=stream)
        inputpdf = PdfFileReader(stream)

        # 3. Loop through each page in the PDF
        for i in range(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            output_stream = io.BytesIO()
            output.write(output_stream)
            output_stream.seek(0)
            output_blob_name = blob_name[:-4]+ "%s.pdf"
            block_blob_service.create_blob_from_stream(container_name=output_container, blob_name=output_blob_name % i, stream=output_stream)

    # 4. Return HTTP Response
    body = {
        'account_name': account_name,
        'input_container': input_container,
        'output_container': output_container,
        'blob_name': blob_name,
        'account_key': 'YOUR_SECRET_ACCOUNT_KEY' if account_key else None
    }
    return func.HttpResponse(json.dumps(body),headers={'Content-Type':'application/json'})
