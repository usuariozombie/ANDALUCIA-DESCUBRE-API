# -*- coding: utf-8 -*-

import fastapi
from fastapi import HTTPException, Request
from typing import List, Optional
from utils.database import MySQL
from pydantic import BaseModel
from utils.easify import GetMSG, Now
from utils.files import JSON
from utils.security import IP

TownsRouter = fastapi.APIRouter()

class TownBase(BaseModel):
	townName: str
	townDescription: Optional[str] = None
	townImage: str
	townMap: Optional[str] = None
	townProvince: Optional[str] = None
	townVisibility: Optional[bool] = True

class TownCreate(TownBase):
	pass

class Town(TownBase):
	townId: int

class DishBase(BaseModel):
	dishName: str
	dishDescription: Optional[str] = None
	dishImage: Optional[str] = None

class DishCreate(DishBase):
	pass

class Dish(DishBase):
	dishId: int
	townId: int

class MonumentBase(BaseModel):
	monumentName: str
	monumentDescription: Optional[str] = None
	monumentImage: Optional[str] = None

class MonumentCreate(MonumentBase):
	pass

class Monument(MonumentBase):
	monumentId: int
	townId: int

class EventBase(BaseModel):
	eventName: str
	eventDate: Optional[str] = None
	eventDescription: Optional[str] = None

class EventCreate(EventBase):
	pass

class Event(EventBase):
	eventId: int
	townId: int

async def log_action(user_id, user_ip, description, action_type):
	MySQL.AddItem(
		"AD_LOGS",
		["userID", "userIP", "logDate", "description", "type"],
		[user_id, user_ip, Now(), description, action_type]
	)

@TownsRouter.post("/towns", response_model=Town)
async def create_town(request: Request):
	try:
		request_json: dict = await request.json()
	except Exception as e:
		MySQL.LogError("/towns", None, IP.Extract(request), Now(), e, "csrf_attempt")
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("towns.no_json")})
	
	townName = request_json.get("townName")
	townDescription = request_json.get("townDescription")
	townImage = request_json.get("townImage")
	townMap = request_json.get("townMap")
	townProvince = request_json.get("townProvince")
	townVisibility = request_json.get("townVisibility", True)

	if not townName:
		return fastapi.responses.JSONResponse(status_code=400, content={"status": 400, "message": GetMSG("towns.invalid_data")})
	if MySQL.ValueExists("AD_TOWNS", "townName", townName):
		return fastapi.responses.JSONResponse(status_code=409, content={"status": 409, "message": GetMSG("towns.already_exists")})
	
	try:
		new_town_id = MySQL.GetLastID("AD_TOWNS", "townId") + 1
		MySQL.AddTown(new_town_id, townName, townDescription, townImage, townMap, townProvince, townVisibility)
		
		await log_action(new_town_id, IP.Extract(request), "Town created", "create_town")
		
		return fastapi.responses.JSONResponse(status_code=200, content={
			"townId": new_town_id, "townName": townName, "townDescription": townDescription, 
			"townImage": townImage, "townMap": townMap, "townProvince": townProvince, "townVisibility": townVisibility})
	except Exception as e:
		print(e)
		return fastapi.responses.JSONResponse(status_code=500, content={"status": 500, "message": GetMSG("towns.error")})

@TownsRouter.get("/towns", response_model=List[Town])
async def get_towns():
	try:
		towns = MySQL.FetchAll("SELECT townId, townName, townDescription, townImage, townMap, townProvince, townVisibility FROM AD_TOWNS")
		print("Towns fetched from database:", towns)
		
		return [Town(townId=town[0], townName=town[1], townDescription=town[2], townImage=town[3], 
					 townMap=town[4], townProvince=town[5], townVisibility=town[6]) for town in towns]
	except Exception as e:
		print("Error fetching towns:", str(e))
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.get("/towns/random/{town_count}", response_model=List[Town])
async def get_randomtowns(town_count: int):
	try:
		towns = MySQL.FetchAll("SELECT townId, townName, townDescription, townImage, townMap, townProvince FROM AD_TOWNS WHERE townVisibility = 1 ORDER BY RAND() LIMIT %s", (town_count,))
		print("Towns fetched from database:", towns)
		
		return [Town(townId=town[0], townName=town[1], townDescription=town[2], townImage=town[3], 
					 townMap=town[4], townProvince=town[5]) for town in towns]
	except Exception as e:
		print("Error fetching towns:", str(e))
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.get("/towns/{town_id}", response_model=Town)
async def get_town(town_id: int):
	try:
		town = MySQL.FetchOne("SELECT townId, townName, townDescription, townImage, townMap, townProvince, townVisibility FROM AD_TOWNS WHERE townId = %s", (town_id,))
		if not town:
			raise HTTPException(status_code=404, detail="Town not found")
		return Town(townId=town[0], townName=town[1], townDescription=town[2], townImage=town[3], 
					townMap=town[4], townProvince=town[5], townVisibility=town[6])
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.put("/towns/{town_id}", response_model=Town)
async def update_town(town_id: int, town: TownCreate, request: Request):
	try:
		if not MySQL.ValueExists("AD_TOWNS", "townId", town_id):
			raise HTTPException(status_code=404, detail="Town not found")
  
		MySQL.UpdateItem(
			"AD_TOWNS",
			["townName", "townDescription", "townImage", "townMap", "townProvince", "townVisibility"],
			[town.townName, town.townDescription, town.townImage, town.townMap, town.townProvince, town.townVisibility],
			"townId",
			[town_id]
		)

		await log_action(town_id, IP.Extract(request), "Town updated", "update_town")
		
		return {"townId": town_id, **town.dict()}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.delete("/towns/{town_id}", response_model=dict)
async def delete_town(town_id: int, request: Request):
	try:
		if not MySQL.ValueExists("AD_TOWNS", "townId", town_id):
			raise HTTPException(status_code=404, detail="Town not found")

		MySQL.Delete("AD_TOWNS", "townId", town_id)

		await log_action(town_id, IP.Extract(request), "Town deleted", "delete_town")

		return {"status": "success", "message": "Town deleted successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.get("/towns/{town_id}/dishes", response_model=List[Dish])
async def get_town_dishes(town_id: int):
	try:
		dishes = MySQL.FetchAll("SELECT dishId, dishName, dishDescription, dishImage, townId FROM AD_DISHES WHERE townId = %s", (town_id,))
		return [Dish(dishId=dish[0], dishName=dish[1], dishDescription=dish[2], dishImage=dish[3], townId=dish[4]) for dish in dishes]
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.post("/towns/{town_id}/dishes", response_model=Dish)
async def create_town_dish(town_id: int, dish: DishCreate, request: Request):
	try:
		new_dish_id = MySQL.GetLastID("AD_DISHES", "dishId") + 1
		MySQL.AddItem(
			"AD_DISHES",
			["dishId", "dishName", "dishDescription", "dishImage", "townId"],
			[new_dish_id, dish.dishName, dish.dishDescription, dish.dishImage, town_id]
		)
		
		await log_action(town_id, IP.Extract(request), "Dish created", "create_dish")

		return {"dishId": new_dish_id, "dishName": dish.dishName, "dishDescription": dish.dishDescription, "dishImage": dish.dishImage, "townId": town_id}
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.delete("/towns/{town_id}/dishes/{dish_id}", response_model=dict)
async def delete_town_dish(town_id: int, dish_id: int, request: Request):
	try:
		if not MySQL.ValueExists("AD_DISHES", "dishId", dish_id):
			raise HTTPException(status_code=404, detail="Dish not found")

		MySQL.Delete("AD_DISHES", "dishId", dish_id)

		await log_action(town_id, IP.Extract(request), "Dish deleted", "delete_dish")
			
		return {"status": "success", "message": "Dish deleted successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.get("/towns/{town_id}/monuments", response_model=List[Monument])
async def get_town_monuments(town_id: int):
	try:
		monuments = MySQL.FetchAll("SELECT monumentId, monumentName, monumentDescription, monumentImage, townId FROM AD_MONUMENTS WHERE townId = %s", (town_id,))
		return [Monument(monumentId=monument[0], monumentName=monument[1], monumentDescription=monument[2], monumentImage=monument[3], townId=monument[4]) for monument in monuments]
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.post("/towns/{town_id}/monuments", response_model=Monument)
async def create_town_monument(town_id: int, monument: MonumentCreate, request: Request):
	try:
		new_monument_id = MySQL.GetLastID("AD_MONUMENTS", "monumentId") + 1
		MySQL.AddItem(
			"AD_MONUMENTS",
			["monumentId", "monumentName", "monumentDescription", "monumentImage", "townId"],
			[new_monument_id, monument.monumentName, monument.monumentDescription, monument.monumentImage, town_id]
		)

		await log_action(town_id, IP.Extract(request), "Monument created", "create_monument")

		return {"monumentId": new_monument_id, "monumentName": monument.monumentName, "monumentDescription": monument.monumentDescription, "monumentImage": monument.monumentImage, "townId": town_id}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.delete("/towns/{town_id}/monuments/{monument_id}", response_model=dict)
async def delete_town_monument(town_id: int, monument_id: int, request: Request):
	try:
		if not MySQL.ValueExists("AD_MONUMENTS", "monumentId", monument_id):
			raise HTTPException(status_code=404, detail="Monument not found")

		MySQL.Delete("AD_MONUMENTS", "monumentId", monument_id)

		await log_action(town_id, IP.Extract(request), "Monument deleted", "delete_monument")
			
		return {"status": "success", "message": "Monument deleted successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.get("/towns/{town_id}/events", response_model=List[Event])
async def get_town_events(town_id: int):
	try:
		events = MySQL.FetchAll("SELECT eventId, eventName, DATE_FORMAT(eventDate, '%Y-%m-%d') as eventDate, eventDescription, townId FROM AD_EVENTS WHERE townId = %s", (town_id,))
		if not events:
			raise HTTPException(status_code=404, detail="No events found for this town")
		return [Event(eventId=event[0], eventName=event[1], eventDate=event[2], eventDescription=event[3], townId=event[4]) for event in events]
	except Exception as e:
		print("Error fetching events:", str(e))
		raise HTTPException(status_code=500, detail="Internal server error while fetching events")

@TownsRouter.post("/towns/{town_id}/events", response_model=Event)
async def create_town_event(town_id: int, event: EventCreate, request: Request):
	try:
		new_event_id = MySQL.GetLastID("AD_EVENTS", "eventId") + 1
		MySQL.AddItem(
			"AD_EVENTS",
			["eventId", "eventName", "eventDate", "eventDescription", "townId"],
			[new_event_id, event.eventName, event.eventDate, event.eventDescription, town_id]
		)

		await log_action(town_id, IP.Extract(request), "Event created", "create_event")

		return {"eventId": new_event_id, "eventName": event.eventName, "eventDate": event.eventDate, "eventDescription": event.eventDescription, "townId": town_id}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@TownsRouter.delete("/towns/{town_id}/events/{event_id}", response_model=dict)
async def delete_town_event(town_id: int, event_id: int, request: Request):
	try:
		if not MySQL.ValueExists("AD_EVENTS", "eventId", event_id):
			raise HTTPException(status_code=404, detail="Event not found")

		MySQL.Delete("AD_EVENTS", "eventId", event_id)

		await log_action(town_id, IP.Extract(request), "Event deleted", "delete_event")
			
		return {"status": "success", "message": "Event deleted successfully"}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
