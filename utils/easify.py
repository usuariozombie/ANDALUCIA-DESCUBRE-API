# -*- coding: utf-8 -*-

import datetime, fastapi, time
from utils.files import JSON
from utils.security import IP

def APILoader(Route : str, Request : fastapi.Request):

	RoutesCFG : dict = JSON.Read("database/routes.json")
	UserIP = IP.Extract(Request)

	if UserIP in RoutesCFG["blacklist"]["*"]: 
		return fastapi.responses.JSONResponse(status_code = 401, content = {"status": 401, "message": GetMSG("api.blacklisted")})

	if Route in RoutesCFG["blacklist"] and UserIP in RoutesCFG["blacklist"][Route]: 
		return fastapi.responses.JSONResponse(status_code = 401, content = {"status": 401, "message": GetMSG("api.blacklisted")})

	if not any(str(Request.url).startswith(EndPoint) for EndPoint in RoutesCFG["endpoints"]): 
		return fastapi.responses.JSONResponse(status_code = 403, content = {"status": 403, "message": GetMSG("api.bad_domain")})

	if not Route in RoutesCFG["whitelist"]: return True 
	
	if UserIP in RoutesCFG["whitelist"]["*"] or UserIP in RoutesCFG["whitelist"][Route]: return True 

	return fastapi.responses.JSONResponse(status_code = 403, content = {"status": 403, "message": GetMSG("api.not_whitelisted")}) 

def GetMSG(Key : str) -> str: return JSON.Read("database/messages.json")[Key]

def Now(Mode = None): return int(time.time()) if Mode == None else datetime.datetime.now().strftime(Mode)