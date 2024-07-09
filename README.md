# DGX-A100-IPMI-Monitoring
A Python tool that monitors built-in temperature sensors of an Nvidia DGX A100 server via IPMI and publishes monitored data via MQTT.

## Requirements:
To use this Python tool, you need:
- An Nvidia DGX A100 server with enabled IPMI/BMC (see IPMI/BNC)
- A docker host (either an external server or a local installation on the DGX A100 server that you want to monitor)
- A MQTT broker

## IPMI/BNC:
Before you can run the Python IPMI monitoring, ensure that the Intelligent Platform Management Interface (IPMI) is accessible. On an Nvidia DGX A100 server, IPMI is implemented and provided by BMC, which should be connected to your network infrastructure via LAN. Use the tool ``ipmitool`` to test the connection to IPMI: ``ipmitool -C 17 -I lanplus -H <bmc_ip_addr> -U ADMIN -P ADMIN <ipmitool_arguments>``. The credentials for accessing IPMI are commonly the credentials for the BMC login.

## Deployment:
Download the content of this repository and modify the configuration properties in ``config.ini`` as follows:
- In section ``[ipmi]``, the property ``Host`` must contain the IP address of your BMC LAN interface. Moreover, replace ``USERNAME`` and ``PASSWORD`` with your credentials to access IPMI/BMC.
- In section ``[broker]``, set the broker hostname or IP address (``Address``) and replace ``MQTT_USER`` and ``MQTT_PASSWORD`` with an MQTT user having write permission to the specified topics.
- Run the docker-compose file


