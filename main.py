# -*- coding: utf-8 -*-

# uvicorn main:AndaluciaDescubreAPI --host 0.0.0.0 --port 44444
# screen -S AndaluciaDescubreAPI uvicorn main:AndaluciaDescubreAPI --host 0.0.0.0 --port 44444

import fastapi
from utils.files import JSON
from utils.security import IP
from utils.easify import APILoader, GetMSG
from fastapi.middleware.cors import CORSMiddleware
from slowapi import errors, Limiter, _rate_limit_exceeded_handler

Config : dict = JSON.Read("config.json")

AndaluciaDescubreAPI = fastapi.FastAPI(
	title = "Andalucia Descubre's API",
	version = "BETA 1.0"
)

APILimiter = Limiter(key_func = IP.Extract)
AndaluciaDescubreAPI.state.limiter = APILimiter
AndaluciaDescubreAPI.add_exception_handler(errors.RateLimitExceeded, _rate_limit_exceeded_handler)
AndaluciaDescubreAPI.add_middleware(CORSMiddleware, allow_origins = Config["cors"], allow_credentials = True, allow_headers = ["*"], allow_methods = ["*"])

from endpoints.auth import AuthRouter
from endpoints.towns import TownsRouter
AndaluciaDescubreAPI.include_router(AuthRouter, prefix = "/auth")
AndaluciaDescubreAPI.include_router(TownsRouter, prefix="/api")

@AndaluciaDescubreAPI.get("/", include_in_schema = True)
async def MainRoute(request: fastapi.Request):
	APIData = APILoader("/", request)
	if APIData != True: return APIData
	return {"andalucia_descubre_debug_your_ip": IP.Extract(request)}

@AndaluciaDescubreAPI.get("/favicon.ico", include_in_schema = False)
async def Favicon(request: fastapi.Request): return fastapi.responses.FileResponse("database/favicon.ico")

@AndaluciaDescubreAPI.exception_handler(404)
async def Error404(request: fastapi.Request, Error: fastapi.HTTPException):
	return fastapi.responses.JSONResponse(status_code = 404, content = {"status": 404, "message": GetMSG("error.404")})

@AndaluciaDescubreAPI.exception_handler(405)
async def Error405(request: fastapi.Request, Error: fastapi.HTTPException):
	return fastapi.responses.JSONResponse(status_code = 405, content = {"status": 405, "message": GetMSG("error.405")})

@AndaluciaDescubreAPI.exception_handler(429)
async def Error429(request: fastapi.Request, Error: fastapi.HTTPException):
	return fastapi.responses.JSONResponse(status_code = 429, content = {"status": 429, "message": GetMSG("error.429").format(Error.detail.split(" per")[0], Error.detail.split(" per ")[1])})

@AndaluciaDescubreAPI.exception_handler(500)
async def Error500(request: fastapi.Request, Error: fastapi.HTTPException):
	return fastapi.responses.JSONResponse(status_code = 500, content = {"status": 500, "message": GetMSG("error.500")})