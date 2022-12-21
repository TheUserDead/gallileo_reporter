import json

def settingsread(type):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    if type == "server":
      outlist = [];
      outlist.append(psettj["server"]["addr"])
      outlist.append(psettj["server"]["archUrl"])
      return outlist
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

def settingsUpdate(what, who, data):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    if what == "archive":
      archsub = psettj["archive"]
      if who == "dateStart":
        archsub["dateStart"] = data
      if who == "dateEnd":
        archsub["dateEnd"] = data
      if who == "dateReported":
        archsub["dateReported"] = data
      psettj["archive"] = archsub 

    if what == "states":
      statessub = psettj["states"]
      if who == "drive":
        statessub["drive"] = data
      if who == "mileage":
        statessub["mileage"] = data
      if who == "wheelCounter":
        statessub["wheelCounter"] = data
      if who == "timeUpdated":
        statessub["timeUpdated"] = data
      psettj["states"] = statessub
    with open("settings_test.json", "w") as outfile:
      json.dump(psettj, outfile, indent=2)
  finally: