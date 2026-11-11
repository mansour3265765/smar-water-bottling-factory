from flask import Flask, render_template, jsonify
import random
from datetime import datetime
app=Flask(__name__)
s={"running":False,"temperature":25.0,"pressure":2.5,"water_level":85.0,"speed":0.0,"bottles":0,"cooling":False,"filling":False,"conveyor":False,"alarms":0,"events":[]}
def log(msg,level="info"):
 s["events"].insert(0,{"time":datetime.now().strftime("%H:%M:%S"),"message":msg,"level":level}); s["events"]=s["events"][:25]
def evaluate():
 if s["temperature"]>80:
  if not s["cooling"]: log("High temperature detected. Cooling activated; production stopped.","danger"); s["alarms"]+=1
  s["cooling"]=True; s["conveyor"]=False; s["filling"]=False
 elif s["temperature"]<35 and s["cooling"]:
  s["cooling"]=False; log("Temperature normalized. Cooling deactivated.")
  if s["running"] and s["pressure"]<7 and s["water_level"]>15: s["conveyor"]=s["filling"]=True
 if s["pressure"]>7:
  if s["conveyor"] or s["filling"]: log("High pressure detected. Production stopped.","danger"); s["alarms"]+=1
  s["conveyor"]=s["filling"]=False
 elif s["pressure"]<5.5 and s["running"] and s["temperature"]<80 and s["water_level"]>15 and not s["cooling"]: s["conveyor"]=s["filling"]=True
 if s["water_level"]<15:
  if s["filling"]: log("Low water level detected. Filling paused.","warning"); s["alarms"]+=1
  s["filling"]=False
 elif s["water_level"]>25 and s["running"] and not s["cooling"] and s["pressure"]<7: s["filling"]=s["conveyor"]=True
def data():
 return {**s,"factory_status":"RUNNING" if s["running"] else "STOPPED","temperature_status":"ABNORMAL" if s["temperature"]>80 else "NORMAL","pressure_status":"ABNORMAL" if s["pressure"]>7 else "NORMAL","water_status":"ABNORMAL" if s["water_level"]<15 else "NORMAL"}
@app.route("/")
def home(): return render_template("index.html")
@app.route("/api/status")
def status(): return jsonify(data())
@app.route("/api/<action>",methods=["POST"])
def actions(action):
 if action=="start":
  s["running"]=True
  if s["temperature"]<=80 and s["pressure"]<=7 and s["water_level"]>=15 and not s["cooling"]: s["conveyor"]=s["filling"]=True
  log("Factory simulation started.")
 elif action=="pause":
  s["running"]=s["conveyor"]=s["filling"]=False; log("Simulation paused.","warning")
 elif action=="reset":
  s.update(running=False,temperature=25.0,pressure=2.5,water_level=85.0,speed=0.0,bottles=0,cooling=False,filling=False,conveyor=False,alarms=0,events=[])
  log("System reset.")
 elif action=="fault-temperature": s["temperature"]=92.0; log("Test fault: high temperature.","danger"); evaluate()
 elif action=="fault-pressure": s["pressure"]=8.5; log("Test fault: high pressure.","danger"); evaluate()
 elif action=="fault-water": s["water_level"]=8.0; log("Test fault: low water level.","warning"); evaluate()
 else: return jsonify(error="Unknown action"),400
 return jsonify(data())
@app.route("/api/tick",methods=["POST"])
def tick():
 if s["running"]:
  s["temperature"]+=random.uniform(-1.8,-.7) if s["cooling"] else random.uniform(-.25,.65)
  s["pressure"]=max(.5,min(10,s["pressure"]+random.uniform(-.12,.12)))
  s["speed"]=max(0,min(75,s["speed"]+random.uniform(-2,2))) if s["conveyor"] else 0
  if s["filling"] and s["conveyor"]: s["water_level"]=max(0,s["water_level"]-random.uniform(.15,.45)); s["bottles"]+=random.randint(1,3)
  else: s["water_level"]=min(100,s["water_level"]+.2)
  evaluate()
 return jsonify(data())
if __name__=="__main__": app.run(debug=True)
