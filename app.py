import pyipmi
import pyipmi.interfaces
import configparser

import threading
import logging

from mqtt import Mqtt
import json
import time
import sys

from datetime import datetime

temp_sensors = {
    0x1: "TEMP_CPU0",
    0x2: "TEMP_CPU1",
    0x3: "TEMP_GB_GPU0",
    0x4: "TEMP_GB_GPU1",
    0x5: "TEMP_GB_GPU2",
    0x6: "TEMP_GB_GPU3",
    0x7: "TEMP_GB_GPU4",
    0x8: "TEMP_GB_GPU5",
    0x9: "TEMP_GB_GPU6",
    0xA: "TEMP_GB_GPU7",
    0x11: "TEMP_GB_HSC0",
    0x23: "TEMP_PLX0",
    0x24: "TEMP_PLX1",
    0x25: "TEMP_PLX2",
    0x26: "TEMP_PLX3",
    0x27: "TEMP_U.2_NVME0",
    0x28: "TEMP_U.2_NVME1",
    0x29: "TEMP_U.2_NVME2",
    0x2A: "TEMP_U.2_NVME3",
    0x2B: "TEMP_U.2_NVME4",
    0x2C: "TEMP_U.2_NVME5",
    0x2D: "TEMP_U.2_NVME6",
    0x2E: "TEMP_U.2_NVME7",
    0x2F: "TEMP_PSU0",
    0x30: "TEMP_PSU1",
    0x31: "TEMP_PSU2",
    0x32: "TEMP_PSU3",
    0x33: "TEMP_PSU4",
    0x34: "TEMP_PSU5",
    0x35: "TEMP_PDB0",
    0x36: "TEMP_PDB1",
    0x37: "TEMP_MB_OUTLET",
    0x38: "TEMP_MB_INLET",
    0x39: "TEMP_CPU0_ABCD",
    0x3A: "TEMP_CPU_EFGH",
    0x3B: "TEMP_CPU1_IJKL",
    0x3C: "TEMP_CPU1_MNOP",
    0x3D: "TEMP_AMBIENT",
    0x3F: "TEMP_RISER",
    0x44: "TEMP_GB_GPU0_M",
    0x45: "TEMP_GB_GPU1_M",
    0x46: "TEMP_GB_GPU2_M",
    0x47: "TEMP_GB_GPU3_M",
    0x48: "TEMP_GB_GPU4_M",
    0x49: "TEMP_GB_GPU5_M",
    0x4A: "TEMP_GB_GPU6_M",
    0x4B: "TEMP_GB_GPU7_M",
    0x4C: "TEMP_MB_AD_CARD0",
    0x4D: "TEMP_MB_AD_CARD1",
    0x4E: "TEMP_IO0_IB6",
    0x4F: "TEMP_IO0_IB7",
    0x50: "TEMP_IO1_IB0",
    0x51: "TEMP_IO1_IB1",
    0x52: "TEMP_IO0_IB8",
    0x53: "TEMP_IO0_IB9",
    0x54: "TEMP_IO1_IB2",
    0x55: "TEMP_IO1_IB3",
    0xE0: "TEMP_IO0_IB0_P0",
    0xE1: "TEMP_IO0_IB1_P0",
    0xE2: "TEMP_IO1_IB2_P0",
    0xE3: "TEMP_IO1_IB3_PO",
    0xE4: "TEMP_IO0_IB4_PO",
    0xE5: "TEMP_IO0_IB5_PO",
    0xE6: "TEMP_IO1_IB6_P0",
    0xE7: "TEMP_IO1_IB7_P0",
    0xEB: "TEMP_MB_AD_C1_P1"
}

def read_sensors(cancel_event,configuration,mqtt):
    logging.info("Monitoring started")
    while not cancel_event.is_set():
        start = time.time()
        try:
            logging.info("Establish IPMI connection ...")
            interface = pyipmi.interfaces.create_interface('ipmitool', interface_type=configuration.get("ipmi","Interface"))
            connection = pyipmi.create_connection(interface)
            connection.session.set_session_type_rmcp(configuration.get("ipmi","Host"), port=configuration.getint("ipmi","Port"))
            connection.session.set_auth_type_user(configuration.get("ipmi","User"), configuration.get("ipmi","Password"))
            connection.session.establish()
            logging.info("Connection established")
            res_payload = {
                "time": datetime.now().isoformat()
            }
            
            for i in temp_sensors.keys():
                temp = connection.get_sensor_reading(i)[0]
                res_payload[temp_sensors[i]] = temp
                if i == 0x1 or i == 0x2:
                    logging.info(temp_sensors[i]+": "+str(temp))
                    
                
            mqtt.publish_async(configuration.get("broker","TempSensorTopic"),json.dumps(res_payload))   
            
            
            connection.session.close()
        except Exception as e:
            logging.error("Error: ",str(e))
            res_payload = {
                "error": str(e)
            }
            mqtt.publish_async(configuration.get("broker","ErrorTopic"),json.dumps(res_payload))
        end = time.time()
        
        dif = end-start
        
        interval = configuration.getint("ipmi","intervall") - dif
        if interval > 0:
            time.sleep(interval)

if __name__ == "__main__":
    print("Starting IPMI Monitoring")
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(stream=sys.stdout, format=format, level=logging.INFO,datefmt="%H:%M:%S")
    
    configuration = configparser.ConfigParser()
    configuration.read("config.ini")
    
    cancel_event = threading.Event()
    
    mqtt = Mqtt()
    mqtt.connect(configuration.get("broker","Address"),configuration.getint("broker","Port"),configuration.get("broker","DeviceId"),configuration.get("broker","Username"),configuration.get("broker","Password"))
  
    ipmi_monitoring_thread = threading.Thread(target=read_sensors, args=(cancel_event,configuration,mqtt), daemon=False)
    ipmi_monitoring_thread.start()
    mqtt.start(cancel_event) # This call blocks the execution