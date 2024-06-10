import fastapi
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.files import JSON
from jwtconfig import create_access_token, decode_access_token
from utils.database import MySQL
from utils.security import InputValidator, IP
from utils.easify import GetMSG, Now
import hashlib
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

AuthRouter = fastapi.APIRouter()
security = HTTPBearer()

smtp_server = "smtp.sendgrid.net"
smtp_port = 587 
smtp_username = "apikey"
Config: dict = JSON.Read("config.json")
smtp_password = Config["keys"]["SENDGRID_API_KEY"]

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
	token = credentials.credentials
	payload = decode_access_token(token)
	if payload is None:
		raise HTTPException(status_code=401, detail="Token inválido o expirado")
	return payload

async def log_action(user_id: int, user_ip: str, description: str, action_type: str):
	try:
		MySQL.AddItem("AD_LOGS", ["userID", "userIP", "logDate", "description", "type"], [user_id, user_ip, Now(), description, action_type])
	except Exception as error:
		print(f"Error logging action: {error}")

@AuthRouter.post("/register", include_in_schema=True)
async def register(request: fastapi.Request):
	try:
		RequestJSON: dict = await request.json()
	except Exception as Error:
		MySQL.LogError("/auth/register", None, IP.Extract(request), Now(), Error, "csrf_attempt")
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_json")})

	Email = RequestJSON.get("email") if InputValidator.Email(RequestJSON.get("email")) == True else False
	Password = RequestJSON.get("password") if InputValidator.Password(RequestJSON.get("password")) == True else False
	TownID = RequestJSON.get("townID")
	Role = RequestJSON.get("role", "user")

	if Email == False:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_email")})
	if Password == False:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_password")})

	if MySQL.ValueExists("AD_USERS", "email", Email) == True:
		return fastapi.responses.JSONResponse(status_code=409, content={"status": 409, "message": GetMSG("register.already_registered")})

	try:
		user_id = MySQL.GetLastID("AD_USERS", "userID") + 1
		MySQL.Register(user_id, IP.Extract(request), Email, hashlib.sha512(Password.encode("utf-8")).digest().hex(), TownID, JSON.Stringify({"requested": Now()}), Role)
		token = create_access_token({"email": Email, "role": Role})
		
		await log_action(user_id, IP.Extract(request), "User registered", "register")

		return {"access_token": token}
	except Exception as Error:
		MySQL.LogError("/auth/register", None, IP.Extract(request), Now(), Error, "mysql_error")
		return fastapi.responses.JSONResponse(status_code=500, content={"status": 500, "message": GetMSG("register.bad")})

@AuthRouter.post("/login", include_in_schema=True)
async def login(request: fastapi.Request):
	try:
		RequestJSON: dict = await request.json()
	except Exception as Error:
		MySQL.LogError("/auth/login", None, IP.Extract(request), Now(), Error, "csrf_attempt")
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_json")})

	Email = RequestJSON.get("email") if InputValidator.Email(RequestJSON.get("email")) == True else False
	Password = RequestJSON.get("password") if InputValidator.Password(RequestJSON.get("password")) == True else False

	if Email == False:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_email")})
	if Password == False:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_password")})

	if MySQL.ValueExists("AD_USERS", "email", Email) == False:
		return fastapi.responses.JSONResponse(status_code=404, content={"status": 404, "message": GetMSG("login.no_account")})

	user_data = MySQL.FetchOne("SELECT userID, password, role, townID, verified FROM AD_USERS WHERE email = %s", (Email,))
	user_id, stored_password, role, townID, verified = user_data

	if verified == 0:
		return fastapi.responses.JSONResponse(status_code=403, content={"status": 403, "message": "Account not verified. Please verify your account."})

	if hashlib.sha512(Password.encode("utf-8")).digest().hex() != stored_password:
		return fastapi.responses.JSONResponse(status_code=401, content={"status": 401, "message": GetMSG("login.invalid_password")})

	token = create_access_token({"email": Email, "role": role, "townID": townID})

	await log_action(user_id, IP.Extract(request), "User logged in", "login")

	return {"access_token": token}

@AuthRouter.get("/user-info", dependencies=[Depends(get_current_user)])
async def user_info(user: dict = Depends(get_current_user)):
	email = user.get("email")
	return {"user_info": email}

@AuthRouter.get("/users", include_in_schema=True)
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != 'admin':
        raise HTTPException(status_code=403, detail="Access denied: Only admins can access user data")
    
    try:
        result = MySQL.FetchAll('SELECT u.userID, u.email, u.townID, u.dates, u.verified, t.townName, t.townImage FROM AD_USERS u LEFT JOIN AD_TOWNS t ON u.townID = t.townId')
        users = [
            {
                "userID": user[0],
                "email": user[1],
                "townID": user[2],
                "dates": json.loads(user[3]),
                "verified": user[4],
                "townName": user[5],
                "townImage": user[6]
            } for user in result
        ]
        return users
    except Exception as e:
        print("Error fetching users:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@AuthRouter.post("/admin/login", include_in_schema=True)
async def admin_login(request: fastapi.Request):
	try:
		RequestJSON: dict = await request.json()
	except Exception as Error:
		MySQL.LogError("/auth/admin/login", None, IP.Extract(request), Now(), Error, "csrf_attempt")
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_json")})

	Email = RequestJSON.get("email") if InputValidator.Email(RequestJSON.get("email")) == True else False
	Password = RequestJSON.get("password") if InputValidator.Password(RequestJSON.get("password")) == True else False

	if Email == False:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_email")})
	if Password == False:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("auth.no_password")})

	if MySQL.ValueExists("AD_USERS", "email", Email) == False:
		return fastapi.responses.JSONResponse(status_code=404, content={"status": 404, "message": GetMSG("login.no_account")})

	user_data = MySQL.FetchOne("SELECT userID, password, role FROM AD_USERS WHERE email = %s", (Email,))
	user_id, stored_password, role = user_data

	if hashlib.sha512(Password.encode("utf-8")).digest().hex() != stored_password:
		return fastapi.responses.JSONResponse(status_code=401, content={"status": 401, "message": GetMSG("login.invalid_password")})

	if role != 'admin':
		return fastapi.responses.JSONResponse(status_code=403, content={"status": 403, "message": "Access denied: Admins only."})

	token = create_access_token({"email": Email, "role": role})

	await log_action(user_id, IP.Extract(request), "Admin logged in", "admin_login")

	return {"access_token": token}

@AuthRouter.put("/user/{user_id}", include_in_schema=True)
async def update_user(user_id: int, request: Request, current_user: dict = Depends(get_current_user)):
	if current_user.get("role") != 'admin':
		raise HTTPException(status_code=403, detail="Access denied: Only admins can update user data")

	try:
		request_json = await request.json()
	except Exception as error:
		raise HTTPException(status_code=400, detail="Invalid JSON")

	update_data = {}
	if "email" in request_json:
		update_data["email"] = request_json["email"]
	if "password" in request_json:
		update_data["password"] = hashlib.sha512(request_json["password"].encode("utf-8")).digest().hex()
	if "role" in request_json:
		update_data["role"] = request_json["role"]
	if "townID" in request_json:
		update_data["townID"] = request_json["townID"]
	if "verified" in request_json:
		update_data["verified"] = request_json["verified"]

	if not update_data:
		raise HTTPException(status_code=400, detail="No valid fields to update")

	columns = list(update_data.keys())
	values = list(update_data.values())

	try:
		MySQL.UpdateItem("AD_USERS", columns, values, "userID", (user_id,))

		# Log action
		await log_action(user_id, IP.Extract(request), "User updated", "update_user")

		return {"status": "success", "message": "User updated successfully"}
	except Exception as error:
		MySQL.LogError("/auth/user/update", user_id, IP.Extract(request), Now(), error, "mysql_error")
		raise HTTPException(status_code=500, detail="An error occurred while updating the user")

@AuthRouter.delete("/user/{user_id}", include_in_schema=True)
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
	if current_user.get("role") != 'admin':
		raise HTTPException(status_code=403, detail="Access denied: Only admins can delete user data")

	try:
		MySQL.Delete("AD_USERS", "userID", user_id)

		# Log action
		await log_action(user_id, IP.Extract(current_user), "User deleted", "delete_user")

		return {"status": "success", "message": "User deleted successfully"}
	except Exception as error:
		MySQL.LogError("/auth/user/delete", user_id, IP.Extract(current_user), Now(), error, "mysql_error")
		raise HTTPException(status_code=500, detail="An error occurred while deleting the user")

@AuthRouter.get("/logs", include_in_schema=True)
async def get_logs(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != 'admin':
        raise HTTPException(status_code=403, detail="Access denied: Only admins can access logs")

    try:
        logs = MySQL.FetchAll("SELECT logID, userID, userIP, logDate, description, type FROM AD_LOGS")
        formatted_logs = [
            {
                "logID": log[0],
                "userID": log[1],
                "userIP": log[2],
                "logDate": log[3],
                "description": log[4],
                "type": log[5]
            } for log in logs
        ]
        return formatted_logs
    except Exception as e:
        print("Error fetching logs:", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while fetching logs")
    
    
@AuthRouter.post("/send-email")
async def send_email(request: Request):
    try:
        data = await request.json()
        from_email = data.get("from_email", "admin@andaluciadescubre.com")
        to_email = data["to_email"]
        subject = data["subject"]
        body = data["body"]

        # Crear el mensaje
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Agregar cuerpo del mensaje en formato HTML
        msg.attach(MIMEText(body, "html"))

        # Conectarse al servidor SMTP y enviar el correo
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Iniciar TLS
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            return {"message": "Email sent successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field in request body: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
