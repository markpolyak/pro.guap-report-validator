from api.schemas import ReportDescription, ValidatorResponse, ReportDescriptionWithLink, ValidatorResponseBadRequest
from fastapi import APIRouter, File, UploadFile, Body, Response, status
from api.utils import ValidatorReports, FileUploader
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


router = APIRouter()


@router.post(
    '/api/validation_report_multipart',
    responses={
        200: {'model': ValidatorResponse},
        400: {'model': ValidatorResponseBadRequest},
        422: {'model': ValidatorResponse},
        500: {'model': ValidatorResponse}
    }
)
def report_validation_multipart(response: Response,
                                report_description: ReportDescription = Body(
                                    ...),
                                file: UploadFile = File(...)
                                ):
    try:
        validator_reports = ValidatorReports(
            report_description.dict(), file.filename, file.file)
        if len(validator_reports.validation_report()) == 0:
            # validator_reports.save_report(file.file.read())
            response.status_code = status.HTTP_200_OK
            status_json = "Успешно"
            parser = validator_reports.format_file
            results = validator_reports.validation_report()
        else:
            status_json = "С ошибками"
            parser = validator_reports.format_file
            results = validator_reports.validation_report()
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        return ValidatorResponse(
            status=status_json,
            parser=parser,
            results=results
        )
    except Exception:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ValidatorResponse(
            status='error',
            parser=None,
            results=[]
        )


@router.post('/api/validation_report',
             status_code=200,
             responses={
                 200: {'model': ValidatorResponse},
                 400: {'model': ValidatorResponseBadRequest},
                 422: {'model': ValidatorResponse},
                 500: {'model': ValidatorResponse}
             })
def report_validation(response: Response,
                      report_description: ReportDescriptionWithLink = Body(...)
                      ):
    try:
        file_uploader = FileUploader(
            report_description.report_link, report_description.username, report_description.password)
        file = file_uploader.upload_file()
        status_code_file_uploader = file['status_code']
        if status_code_file_uploader != 200:
            response.status_code = status_code_file_uploader
            status_json = "Ошибка"
            message = file['message']
            parser = None
            results = []
            response_json = ValidatorResponseBadRequest(
                status=status_json, message=message, parser=parser, results=results)
            return JSONResponse(
                status_code=status_code_file_uploader,
                content=jsonable_encoder(response_json)
            )

        validator_reports = ValidatorReports(
            report_description.dict(), file['filename'], file['file_binary'])
        if len(validator_reports.validation_report()) == 0:
            # validator_reports.save_report(file['file_binary'])
            response.status_code = status.HTTP_200_OK
            status_json = "Успешно"
            parser = validator_reports.format_file
            results = validator_reports.validation_report()
        else:
            status_json = "С ошибками"
            parser = validator_reports.format_file
            results = validator_reports.validation_report()
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        return ValidatorResponse(
            status=status_json,
            parser=parser,
            results=results
        )
    except Exception:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ValidatorResponse(
            status='error',
            parser=None,
            results=[]
        )
