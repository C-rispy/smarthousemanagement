from smart_house import *
import time
import sys

def test_toggle_status():
    for name, obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            if "status" not in obj: 
                continue

            original_status = obj["status"]
            call(obj, "toggle_status")

            expected = "off" if original_status == "on" else "on"
            if obj["status"] != expected:
                raise AssertionError(f"{name} did not toggle correctly. Expected {expected}, got {obj['status']}")
 
            call(obj, "toggle_status") # toggle back to restore original state
            if obj["status"] != original_status:
                raise AssertionError(f"{name} failed to toggle back to {original_status}")

def test_get_power_consumption():
    for name, obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            if obj["status"] == "off":
                continue
            
            match obj["_classname"]:
                case "Light":
                    expected_value = round(obj["base_power"]*obj["brightness"]/100)
                
                case "Thermostat":
                    expected_value = obj["base_power"]*abs(obj["target_temperature"] - obj["room_temperature"])
                
                case "Camera":
                    expected_value = obj["base_power"] * obj["resolution_factor"]
                
                case _:
                    print("Unknown device type")
            
            actual_value = call(obj, "get_power_consumption")
            if actual_value !=  expected_value:
                raise AssertionError(f"{name} power consumption calculation error: expected {expected_value}, got {actual_value}")

def test_set_target_temperature():
    for name, obj in globals().items():
        if name.startswith("thermostat"):
            call(obj, "set_target_temperature", 27)
            expected_temperature = 27
            actual_temperature = obj["target_temperature"]
            if actual_temperature != expected_temperature:
                raise AssertionError(f"Set target temperature error: expected {expected_temperature} degree Celsius, got {actual_temperature} degree Celsius")

def test_get_target_temperature():
    for name, obj in globals().items():
        if name.startswith("thermostat"):
            call(obj, "set_target_temperature", 27) #test_set_target_temperature need to be done before this test
            expected_temperature = 27
            actual_temperature = call(obj, "get_target_temperature")
            if actual_temperature != expected_temperature:
                raise AssertionError(f"Get target temperature error: {expected_temperature} degree Celsius, got {actual_temperature} degree Celsius")

def test_describe_device():
    for name, obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            classname = obj["_classname"]
            device_name = obj.get("name")
            location = obj.get("location")
            status = obj.get("status")
            connection = call(obj,"describe_connection") if classname != "Light" else ""

            match obj["_classname"]:
                case "Light":
                    brightness = obj.get("brightness")
                    expected_describe = f"The {device_name} {classname} is located in {location}, is currently {status}, and is currently set to {brightness}% brightness"
                case "Thermostat":
                    room_temp = obj.get("room_temperature")
                    target_temp = obj.get("target_temperature")
                    expected_describe = f"The {device_name} {classname} is located in {location}, is currently set to {target_temp} degree Celsius in a {room_temp} degree room. {connection}"
                case "Camera":
                    if obj.get("resolution_factor") < 5: resolution = "low"
                    elif obj.get("resolution_factor") < 10: resolution = "medium"
                    else: resolution = "high"
                    expected_describe = f"The {device_name} {classname} is located in {location}, is currently {status}, and has a {resolution} resolution sensor. {connection}"
                case _:
                    raise AssertionError("Unknown device type") 
                 
            actual_describe = call(obj, "describe_device")
            if actual_describe != expected_describe:
                raise AssertionError(f"Get describe device error: expected: {expected_describe}, get {actual_describe}")
        
def test_connect():
    for name, obj in globals().items():
        if name.startswith(("thermostat", "camera")):
            call(obj,"connect","10.10.10.4")
            expected_ip = "10.10.10.4"
            actual_ip = obj["ip"]
            if actual_ip != expected_ip:
                raise AssertionError(f"Get connect error: expected connected ip: {expected_ip}, get{actual_ip}")
            
def test_is_connected():
    for name, obj in globals().items():
        if name.startswith(("thermostat", "camera")):
            call(obj, "connect", "10.10.10.4")
            if obj["connected"] != True:
                raise AssertionError(f"Get connected status error: expected True, get False")
    
def test_disconnect():
    for name, obj in globals().items():
        if name.startswith(("thermostat", "camera")):
            call(obj, "disconnect")
            if obj["connected"] != False:
                raise AssertionError(f"Get connected status error: expected False, get True")
    
def test_describe_connection():
    for name, obj in globals().items():
        if name.startswith(("thermostat", "camera")):
            if "ip" not in obj or not obj["connected"]:
                expected_connection_describe = "It is currently disconnected."
            else:
                expected_connection_describe = f"It is currently connected to server {obj['ip']}."
            actual_connection_describe = call(obj, "describe_connection")
            if actual_connection_describe != expected_connection_describe:
                raise AssertionError(f"Get connection describe error: expected: {expected_connection_describe}, get {actual_connection_describe}")


def test_get_all_device_descriptions():
    all_desc = call(temp_management, "get_all_device_descriptions")
    if not isinstance(all_desc, list):
        raise AssertionError("Expected list from get_all_device descriptions, received other object")
    if not all(isinstance(d,str) for d in all_desc):
        raise AssertionError("Returned descriptions aren't all strings")
    
    light_desc = call(temp_management, "get_all_device_descriptions", search_type = "Light")
    therm_desc = call(temp_management, "get_all_device_descriptions", search_type = "Thermostat")
    camera_desc = call(temp_management, "get_all_device_descriptions", search_type = "Camera")
    living_room_desc = call(temp_management, "get_all_device_descriptions", search_room = "Living room")
    for name,obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            match obj['_classname']:
                case "Light":
                    if call(obj,"describe_device") not in light_desc:
                        raise AssertionError(f"Description of {obj['name']} not in get_all_device_description of Light objects")
                case "Thermostat":
                    if call(obj,"describe_device") not in therm_desc:
                        raise AssertionError(f"Description of {obj['name']} not in get_all_device_description of Thermostat objects")
                case "Camera":
                    if call(obj,"describe_device") not in camera_desc:
                        raise AssertionError(f"Description of {obj['name']} not in get_all_device_description of Camera objects")
                case _:
                    raise AssertionError("Unknown Device Type")
            if obj['location'] == 'Living room':
                if call(obj,"describe_device") not in living_room_desc:
                    raise AssertionError(f"Description of {obj['name']} not in get_all_device_description of living room objects")
            
def test_search_type():
    types = {} # this way we don't have to test separate locations, it takes every one created in the setup, same for search_room

    for name,obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            type = obj["_classname"]
            power = call(obj, "get_power_consumption")
            description = call(obj, "describe_device")

            if type not in types:
                types[type] = [0,[]]
            if isinstance(power, (int, float)):
                types[type][0]+= power
            types[type][1].append(description)
    
    for type in types:
        res = types[type]
        expected = call(temp_management, "search_type", type)
        if expected != res:
            raise AssertionError(f'The search for devices of type: "{type}" did not work properly')

def test_search_room():
    rooms = {} 

    for name,obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            room = obj["location"]
            power = call(obj, "get_power_consumption")
            description = call(obj, "describe_device")

            if room not in rooms:
                rooms[room] = [0,[]]
            if isinstance(power, (int, float)):
                rooms[room][0]+= power
            rooms[room][1].append(description)
    
    for room in rooms:
        res = rooms[room]
        expected = call(temp_management, "search_room", room)
        if expected != res:
            raise AssertionError(f"The search for devices in the {room} did not work properly")

def test_calculate_total_power_consumption():

    lights_total_power = call(temp_management, "calculate_total_power_consumption", search_type = "Light")
    thermostats_total_power = call(temp_management, "calculate_total_power_consumption", search_type = "Thermostat")
    cameras_total_power = call(temp_management, "calculate_total_power_consumption", search_type = "Camera")
    studyroom_total_power = call(temp_management,"calculate_total_power_consumption", search_room = "Study Room")
    everything = call(temp_management,"calculate_total_power_consumption")

    tot_pow_lights = 0
    tot_pow_thermostats = 0
    tot_pow_cameras = 0
    tot_pow_studyroom = 0
    tot_pow_all = 0

    for name,obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            
            if obj["_classname"] == "Light":
                    res = call(obj, "get_power_consumption")
                    if isinstance(res, (int,float)):
                        tot_pow_lights += res
                        tot_pow_all += res
            elif obj["_classname"] == "Thermostat":
                    res = call(obj, "get_power_consumption")
                    if isinstance(res, (int,float)):
                        tot_pow_thermostats += res
                        tot_pow_all += res
            elif obj["_classname"] == "Camera":
                    res = call(obj, "get_power_consumption")
                    if isinstance(res, (int,float)):
                        tot_pow_cameras += res
                        tot_pow_all += res
            elif obj["location"] == "Study Room":
                    res = call(obj, "get_power_consumption")
                    if isinstance(res, (int,float)):
                        tot_pow_studyroom += res
                        tot_pow_all += res
            else:
               tot_pow_all += call(obj, "get_power_consumption") 

    if lights_total_power != tot_pow_lights:
        raise AssertionError("The total power consumption of the lights has not been calculated correctly")
    if thermostats_total_power != tot_pow_thermostats:
        raise AssertionError("The total power consumption of the thermostats has not been calculated correctly")
    if cameras_total_power != tot_pow_cameras:
        raise AssertionError("The total power consumption of the lights has not been calculated correctly")
    if studyroom_total_power != tot_pow_studyroom:
        raise AssertionError("The total power consumption of the study room has not been calculated correctly")
    if everything != tot_pow_all:
        raise AssertionError("The total power consumption was not calculated correctly")

def test_get_all_connected_devices():
    call(thermostat_test, "connect","10.10.10.5")
    call(thermostat_test_2,"connect", "10.10.10.4")
    call(camera_test, "connect", "10.10.10.5")
    call(camera_test_2, "connect", "10.10.10.4")

    connected_5 = call(temp_management, "get_all_connected_devices", "10.10.10.5")
    test_connect_5 = [0,[]]
    connected_4 = call(temp_management, "get_all_connected_devices", "10.10.10.4")
    test_connect_4 = [0,[]]
    connected_all = call(temp_management, "get_all_connected_devices")
    test_connect_all = [0,[]]

    for name,obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            if "connected" in obj and obj["connected"] is True and obj["status"] == "on":
                if isinstance(call(obj, "get_power_consumption"),(int,float)):
                    test_connect_all[0] += call(obj, "get_power_consumption")
                test_connect_all[1].append(call(obj,"describe_device"))

            if "connected" in obj and obj["connected"] is True and obj["ip"] == "10.10.10.5" and obj["status"] == "on":
                if isinstance(call(obj, "get_power_consumption"),(int,float)):
                    test_connect_5[0] += call(obj, "get_power_consumption")
                test_connect_5[1].append(call(obj,"describe_device"))
                        
            if "connected" in obj and obj["connected"] is True and obj["ip"] == "10.10.10.4" and obj["status"] == "on":
                if isinstance(call(obj, "get_power_consumption"),(int,float)):
                    test_connect_4[0] += call(obj, "get_power_consumption")
                test_connect_4[1].append(call(obj,"describe_device"))
                        
    
    if connected_5 != test_connect_5:
        raise AssertionError("Devices connected to IP = 10.10.10.5 were not taken correctly")
    if connected_4 != test_connect_4:
        raise AssertionError("Devices connected to IP = 10.10.10.4 were not taken correctly")
    if connected_all != test_connect_all:
        raise AssertionError("Connected devices were not taken correctly")



def test_invalid_call_method():
    for name, obj in globals().items():
        if name.endswith(("_test", "_test_2")):
            try:
                call(obj, "wrong_method")
            except NotImplementedError as e:
                pass
            else:
                raise AssertionError(f"Expected NotImplemented Error, got {e}")

def test_make_invalid_class():
    invalid = {"_classname": "Invalid", "_parent": None}
    obj = make(invalid, "Broken Device", "Toilet", 0, "off", 70)
    try:
        call(obj, get_power_consumption)
    except NotImplementedError:
        pass
    else:
        raise AssertionError(f"Expected NotImplemented error")
    
def test_make():

    temp_lamp = make(Light, "Temp Lamp", "Basement", 200, "off", 100,management=temp_management)
    temp_cam = make(Camera, "Temp Camera", "Basement", 200, "off", 50,management=temp_management)
    temp_therm = make(Thermostat, "Temp Thermostat", "Basement", 800, "on", 50, 20,management=temp_management)

    for obj in temp_management['devices']:
        if not isinstance(obj, dict):
            raise AssertionError("make() should return dictionary")
        for key in ["_class","_classname","location","base_power","status"]:
            if key not in obj:
                raise AssertionError(f"Object {obj['name']} missing key: {key}")
        if obj.get('_classname') == "Light" and "brightness" not in obj:
            raise AssertionError("Object of class Light doesn't have brightness attribute")
        if obj.get('_classname') == "Thermostat" and ("room_temperature" not in obj or "target_temperature" not in obj):
            raise AssertionError("Object of class Thermostat doesn't have the necessary temperature attributes")
        if obj.get('_classname') == "Camera" and "resolution_factor" not in obj:
            raise AssertionError("Object of class Camera doesn't have resolution_factor attribute")
      

def run_tests():
    results = {"pass": 0, "fail": 0, "error": 0}
    start_time = time.time()
    for (name, test) in globals().items():
        if not name.startswith("test_"):
            continue
        if type(test) != type(lambda: None): # for step 03.8
            continue
        if select_param and select_param.lower() not in name.lower():
            continue
        test_start = time.time()
        try:
            test()
            duration = time.time() - test_start
            print(f"[PASS] {name} ({duration:.5f}s)")
            results["pass"] += 1
        except AssertionError as e:
            duration = time.time() - test_start
            print(f"[FAIL] {name}, Error: {e} ({duration:.5f}s)")
            results["fail"] += 1
        except Exception as e:
            duration = time.time() - test_start
            print(f"[ERROR] {name}, Error: {e} ({duration:.5f}s)")
            results["error"] += 1
    total_time = time.time() - start_time
    print(f"\nTotal time: {total_time:.5f}s")
    print(f"pass {results['pass']}")
    print(f"fail {results['fail']}")
    print(f"error {results['error']}")
    

def setup():
    global lamp_test, lamp_test_2, thermostat_test, thermostat_test_2, camera_test, camera_test_2, temp_management
    
    temp_management = {
    "_classname": "temp_management",
    "_parent": None,
    "devices": [],
    "search_type": search_type,
    "search_room": search_room,
    "calculate_total_power_consumption": calculate_total_power_consumption,
    "get_all_device_descriptions": get_all_device_descriptions,
    "get_all_connected_devices": get_all_connected_devices
    }

    lamp_test = make(Light, "Test Lamp", "Bedroom", 100, "off", 50, management=temp_management)
    lamp_test_2 = make(Light, "Test Lamp", "Living room", 80, "on", 40, management=temp_management)
    thermostat_test = make(Thermostat, "Test Thermostat", "Living room", 1000, "off", 15, 20, management=temp_management)
    thermostat_test_2 = make(Thermostat, "Test Thermostat", "Guest room", 800, "on", 10, 28, management=temp_management)
    camera_test = make(Camera, "Test Camera", "Study Room", 400, "off", 50, management=temp_management)
    camera_test_2 = make(Camera, "Test Camera", "Gaming Room", 200, "on", 50, management=temp_management)


def teardown():
    to_delete = [name for name in globals() if name.endswith(("_test", "_test_2"))]
    for name in to_delete:
        del globals()[name]
    del(globals()["temp_management"])
    

if __name__ == "__main__":
    setup()
    test_error = 100000
    test_false = False
    test_true = True
    test_string = "error"
    select_param = None
    if "--select" in sys.argv:
        select_param_index = sys.argv.index("--select") + 1
        if len(sys.argv) > select_param_index:
            select_param = sys.argv[select_param_index]
    run_tests()
    if "--verbose" in sys.argv: # put after tun_tests() in order to also catch variables created in the run_tests() function
        test_xxx = []
        for (name, var) in list(globals().items()): # list, because else test_xxx gets changed during the iteration, which messes with globals().items() (since it's live)
            if not name.startswith("test_"):
                continue
            if type(var) != type(lambda: None): # lambda makes it a lot more comfortable than e.g. type(setup) (because globals().items() would get changed midway through)
                test_xxx.append(name)
        print(test_xxx)
    teardown()
