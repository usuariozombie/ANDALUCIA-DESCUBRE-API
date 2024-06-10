# -*- coding: utf-8 -*-

import fastapi, re, requests
from utils.files import JSON

class IP():
	def Extract(request: fastapi.Request) -> str: return "127.0.0.1" if not request.client or not request.client.host else request.headers["CF-Connecting-IP"] if "CF-Connecting-IP" in request.headers else request.client.host

class InputValidator():

	def Email(Email, MaxLenght : int = 100, MinLength : int = 6):
		if Email == None: return False
		if len(Email) < MinLength or len(Email) > MaxLenght: return False
		if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", Email): return False
		return True

	def Password(Password, MaxLenght : int = 128, MinLength : int = 8):
		if Password == None: return False
		if len(Password) < MinLength or len(Password) > MaxLenght: return False
		if not re.match(r'^[\w!@#$%^&*()_+{}[\]:;"\'<>?,./\\|-]+$', Password): return False
		return len(Password) <= 4096 // 8 - 2 * 64 - 2 

def Captcha(CaptchaData):
	if CaptchaData in [None, "", "undefined"]: return False
	Config : dict = JSON.Read("config.json")	
	CaptchaREQ = requests.post("https://www.google.com/recaptcha/api/siteverify", data = {"secret": Config["captcha"], "response": CaptchaData}).json()
	return False if not CaptchaREQ["success"] else True

