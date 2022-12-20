import json

def settingsread(type):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    if type == "server":
      return psettj["server"]["addr"]
    if type == "mqtt":
      outlist = [];
      outlist.append(psettj["mqtt"]["mqttAddr"])
      outlist.append(psettj["mqtt"]["name"])
      outlist.append(psettj["mqtt"]["pass"])
      return outlist
    if type == "driver":
      outlist = [];
      outlist.append(psettj["driver"]["car_num"])
      outlist.append(psettj["driver"]["driverid"])
      return outlist
    if type == "archive":
      outlist = [];
      outlist.append(psettj["archive"]["dateStart"])
      outlist.append(psettj["archive"]["dateEnd"])
      outlist.append(psettj["archive"]["dateReported"])
      return outlist
    if type == "states":
      outlist = [];
      outlist.append(psettj["states"]["drive"])
      outlist.append(psettj["states"]["mileage"])
      outlist.append(psettj["states"]["wheelCounter"])
      outlist.append(psettj["states"]["timeUpdated"])
      return outlist
  except FileNotFoundError:
    print("Settings file not found!")
    sys.exit()