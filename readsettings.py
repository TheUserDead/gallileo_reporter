import json

if __name__ == "__main__":
  print("This file is module for main program 'trackerconnector.py' and cannot be used directly. \nPlease call mentioned file!")

# REWORK TO RETURN DICT!
def settingsRead(type):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    if type == "server":
      outlist = [];
      outlist.append(psettj["server"]["addr"])
      outlist.append(psettj["server"]["archUrl"])
      outlist.append(psettj["server"]["ftpServer"])
      outlist.append(psettj["server"]["ftpUser"])
      outlist.append(psettj["server"]["ftpPass"])
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
      outlist.append(psettj["archive"]["startDump"])
      outlist.append(psettj["archive"]["dateStart"])
      outlist.append(psettj["archive"]["dateEnd"])
      outlist.append(psettj["archive"]["dateReported"])
      outlist.append(psettj["archive"]["packQueue"])
      outlist.append(psettj["archive"]["profileFile"])
      outlist.append(psettj["archive"]["timeArchHour"])
      return outlist
    if type == "states":
      outlist = [];
      outlist.append(psettj["states"]["drive"])
      outlist.append(psettj["states"]["mileage"])
      outlist.append(psettj["states"]["wheelCounter"])
      outlist.append(psettj["states"]["timeUpdated"])
      return outlist
    if type == "initial":
      outlist = [];
      outlist.append(psettj["initial"]["configured"])
      return outlist
  except FileNotFoundError:
    print("<!> Settings file not found!")
    sys.exit() #rework
  except KeyError:
    print("<!> Something wrong with JSON keys, config is UP to DATE?")
  except TypeError:
    print("<!> Something wrong with JSON keys, config is UP to DATE?")

def settingsUpdate(what, who, data):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    print(what, who, data)
    if what == "archive":
      archsub = psettj["archive"]
      if who == "startDump":
        archsub["startDump"] = data
      if who == "dateStart":
        archsub["dateStart"] = data
      if who == "dateEnd":
        archsub["dateEnd"] = data
      if who == "dateReported":
        archsub["dateReported"] = data
      if who == "packQueue":
        archsub["packQueue"] = data
      if who == "timeArchHour":
        archsub["timeArchHour"] = data
      psettj["archive"] = archsub
    if what == "initial":
      initsub = psettj["initial"]
      if who == "configured":
        initsub["configured"] = data
      psettj["initial"]= initsub
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
    with open("settings.json", "w") as outfile:
      json.dump(psettj, outfile, indent=2)
  finally:
    pass
