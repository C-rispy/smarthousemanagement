def toggle_status(obj):
    current_status = obj.get("status","off")
    if current_status == "on":
        obj["status"] = "off"
    else:
        obj["status"] = "on"
    
def get_power_consumption(obj):
    if obj["status"] == "off":
        return f"No power is consumed, {obj['name']} is off!"

    match obj["_classname"]:
        case "Light":
            consumption = round(obj["base_power"]*obj["brightness"]/100)
        case "Thermostat":
            consumption = obj["base_power"]*abs(obj["target_temperature"] - obj["room_temperature"])
        case "Camera":
             consumption = obj["base_power"] * obj["resolution_factor"]
        case _:
            print("Unknown device type")  
            return 0          
    
    return consumption

def set_target_temperature(obj, temperature):
    obj["target_temperature"] = temperature

def get_target_temperature(obj):
    return obj["target_temperature"]

def describe_device(obj):
    classname = obj["_classname"]
    name = obj.get("name")
    location = obj.get("location")
    status = obj.get("status")
    connection = call(obj,"describe_connection") if classname != "Light" else None

    match classname:
        case "Light":
            brightness = obj.get("brightness")
            return f"The {name} {classname} is located in {location}, is currently {status}, and is currently set to {brightness}% brightness"
        case "Thermostat":
            room_temp = obj.get("room_temperature")
            target_temp = obj.get("target_temperature")
            return f"The {name} {classname} is located in {location}, is currently set to {target_temp} degree Celsius in a {room_temp} degree room. {connection}"
        case "Camera":
            if obj.get("resolution_factor") < 5: resolution = "low"
            elif obj.get("resolution_factor") < 10: resolution = "medium"
            else: resolution = "high"
            return f"The {name} {classname} is located in {location}, is currently {status}, and has a {resolution} resolution sensor. {connection}"
        case _:
            raise ValueError("Unknown device type")  

# abstract methods
def abstract_describe_device(obj):
    raise NotImplementedError(f"{obj['_classname']} must implement describe_device()")

def abstract_get_power_consumption(obj): # removed *args, i dont think it's necessary
    raise NotImplementedError(f"{obj['_classname']} must implement get_power_consumption()")

Device = {
    "name":None,
    "location":None,
    "base_power":None,
    "status":"off", # default status
    "_classname":"Device",
    "_parent":None,
    "toggle_status":toggle_status,
    "get_power_consumption":abstract_get_power_consumption,
    "describe_device": abstract_describe_device
}

def connect(obj,ip):
    if obj["connected"]==True:
        print(f"{obj['name']} is now connected to {obj['ip']}.")
    obj["ip"]=ip
    obj["connected"]=True

def disconnect(obj):
    if obj["connected"]==False:
        print(f"{obj} is already disconnected.")
    obj["connected"]=False

def is_connected(obj):
    return obj["connected"]

def describe_connection(obj): # helper function for describe_device. let me know if you find a better way to do this
    return f"It is currently connected to server {obj['ip']}." if obj['connected'] else "It is currently disconnected."

Connectable = {
    "connected":False,
    "ip":None,
    "connect":connect,
    "disconnect":disconnect,
    "is_connected":is_connected,
    "describe_connection":describe_connection,
    "_parent":None # added to help with find() (later in step 03 testing)
}

Light = {
    "brightness":None,
    "get_power_consumption":get_power_consumption,
    "describe_device":describe_device,
    "_classname":"Light",
    "_parent":Device,
}

Thermostat = {
    "_parent": [Device, Connectable],
    "_classname":"Thermostat",
    "room_temperature": None,
    "target_temperature": None,
    "get_power_consumption": get_power_consumption,
    "describe_device":describe_device,
    "set_target_temperature": set_target_temperature,
    "get_target_temperature": get_target_temperature
}

Camera = {
    "_parent": [Device, Connectable],
    "_classname":"Camera",
    "resolution_factor": None,
    "get_power_consumption": get_power_consumption,
    "describe_device":describe_device
}

def filter_helper(obj,condition):
    devices = [device for device in obj["devices"] if condition(device)]
    total_power = 0
    descriptions = []
    for device in devices:
        power = call(device, "get_power_consumption")
        if isinstance(power, (int,float)):
            total_power += power
        descriptions.append(call(device, "describe_device"))
    return [total_power, descriptions]

def search_type(obj, type):
    return filter_helper(obj, lambda x: x["_classname"] == type)

def search_room(obj, room):
    return filter_helper(obj, lambda x: x["location"] == room)

def calculate_total_power_consumption(obj, search_type = None, search_room = None):
    if search_type is not None and search_room is not None:
        return filter_helper(obj, lambda x: x["_classname"] == search_type and x["location"] == search_room)[0]
    elif search_type is not None:
        return filter_helper(obj, lambda x: x["_classname"] == search_type)[0]
    elif search_room is not None:
        return filter_helper(obj, lambda x: x["location"] == search_room)[0]
    else:
        return filter_helper(obj, lambda x: True)[0]
    

def get_all_device_descriptions(obj, search_type = None, search_room = None):
    if search_type is not None and search_room is not None:
        return filter_helper(obj, lambda x: x["_classname"] == search_type and x["location"] == search_room)[1]
    elif search_type is not None:
        return filter_helper(obj, lambda x: x["_classname"] == search_type)[1]
    elif search_room is not None:
        return filter_helper(obj, lambda x: x["location"] == search_room)[1]
    else:
        return filter_helper(obj, lambda x: True)[1]
    

def get_all_connected_devices(obj, ip = None):
    if ip is not None:
        return filter_helper(obj,lambda x: ("connected" in x and x["connected"] is True and x["ip"] == ip and x["status"] == "on"))
    else:
        return filter_helper(obj,lambda x: ("connected" in x and x["connected"] is True and x["status"] == "on"))

SmartHouseManagement = {
    "_classname": "SmartHouseManagement",
    "_parent": None,
    "devices": [],
    "search_type": search_type,
    "search_room": search_room,
    "calculate_total_power_consumption": calculate_total_power_consumption,
    "get_all_device_descriptions": get_all_device_descriptions,
    "get_all_connected_devices": get_all_connected_devices
}

def call(obj,method_name,*args, **kwargs): #i had to add **kwargs because calculate_total_consumption needs it
    if "_class" in obj: #i had to make the change here to make the SmartHouseManagement work as it does not have "_class", if you see a better way, pls correct
        method = find(obj["_class"],method_name)
    else: 
        method = obj.get(method_name)

    if method is None:
        raise NotImplementedError(f"Method {method_name} not implemented!")
    return method(obj,*args, **kwargs)

def find(cls, method_name):
    if cls is None:
        return None
    if method_name in cls:
        return cls[method_name]
    parents = cls.get("_parent")
    if isinstance(parents, list):
        for parent in parents:
            result = find(parent, method_name)
            if result is not None:
                return result
    elif parents is not None:
        return find(parents, method_name)
    return None # so it enters the next for iteration

def make(cls,name,location,base_power,status,*args,management = SmartHouseManagement):
    obj = {
        "_class":cls,
        "_classname": cls["_classname"],
        "name":name,
        "location":location,
        "base_power":base_power,
        "status":status
    }
    if cls["_classname"] == "Light":
        obj["brightness"] = args[0]
    
    elif cls["_classname"] == "Thermostat":
        obj["room_temperature"] = args[0]
        obj["target_temperature"] = args[1]
        obj["connected"] = False
        obj["ip"] = None

    elif cls["_classname"] == "Camera":
        obj["resolution_factor"] = args[0]
        obj["connected"] = False
        obj["ip"] = None
    
    management["devices"].append(obj) #every Device gets immediately added to the SmartHouseManagement system at its creation

    return obj

'''lamp1 = make(Light, "ZEST Smart Lamp", "living room", 300, "off", 70)
call(lamp1, "toggle_status")
print(call(lamp1, "get_power_consumption"))
print(call(lamp1, "describe_device"))
print(call(SmartHouseManagement, "calculate_total_power_consumption", search_room = "living room"))
print(call(SmartHouseManagement, "calculate_total_power_consumption", search_type = "Light"))
print(call(SmartHouseManagement, "calculate_total_power_consumption"))

thermostat1 = make(Thermostat, "ZEST Smart Thermo", "bedroom", 100, "on", 5, 20)
thermostat2 = make(Thermostat, "ZEST Smart Thermo2", "living room", 100, "on", 5, 20)
print(call(SmartHouseManagement, "get_all_device_descriptions", search_type = "Thermostat"))
print(call(SmartHouseManagement, "get_all_device_descriptions", search_type = "Thermostat", search_room = "living room"))
call(thermostat1,"connect","10.10.10.4")
print(call(thermostat1, "get_power_consumption"))
print(call(SmartHouseManagement, "calculate_total_power_consumption"))
call(thermostat1, "set_target_temperature", 22)
print(call(thermostat1, "get_target_temperature"))
print(call(thermostat1, "describe_device"))

camera1 = make(Camera, "ZEST Smart Cam", "bathroom", 200, "off", 200)
print(call(camera1, "get_power_consumption"))
print(call(camera1, "describe_device"))

lamp2 = make(Light, "ZEST Smart Lamp2", "bedroom", 300, "on", 70)
print(call(lamp2, "get_power_consumption"))

camera2 = make(Camera, "ZEST Smart Cam 2", "living room", 200, "off", 200)
call(camera2, "toggle_status")
call(camera1,"connect","10.10.10.4")
call(camera1, "toggle_status")
print(call(camera1, "get_power_consumption"))
print(call(SmartHouseManagement, "get_all_connected_devices", ip = "10.10.10.4"))
print(call(SmartHouseManagement, "get_all_connected_devices"))
print(call(SmartHouseManagement, "search_room", "bedroom"))
print(call(SmartHouseManagement, "search_type", "Light"))
call(camera1, "connect", "10.10.10.4")
print(call(camera1, "describe_device"))
print(call(lamp1, "describe_device"))'''