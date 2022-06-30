from api.schemas import ReportDescription, ValidatorResponse, ReportDescriptionWithLink, ValidatorResponseBadRequest
from fastapi import APIRouter, File, UploadFile, Body, Response, status
from api.utils import ValidatorReports, FileUploader
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


router = APIRouter()
