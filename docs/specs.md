# Specification

## Machine Selector

This widget lets the user choose between multiple machines to monitor and control.  

It displays the name of the currently selected machine.
If multiple machines are detected, clicking on the widget will show a dropdown list of all available machines.

We can implement this with :  

>def get_machines():  
    """  
    GET /machines  
    Returns a list of all available machines with their names.  
    """  
    pass

---

## Machine Information

This widget allows the user to view the machine's identification and status, and to reboot the machine with a button.

The widget will display the machine's name, its online or offline status, the client ID, machine ID, software-defined radio device, and IP address.

We can implement this with : 

>def get_machine_details(id: str):  
    """  
    GET /machine/{id}  
    Returns the details of the selected machine including name, status, client ID, machine ID, SDR device, and IP.  
    """  
    pass

-

>def post_machine_reboot(id: str):  
    """  
    POST /machine/{id}/reboot  
    Triggers a reboot of the selected machine.  
    """  
    pass

---

## 5G Core Network

This widget allows the user to view and interact with the 5G core network.

The widget displays the 5G core network status: stopped, starting, or running.
It also allows the user to start, restart, or stop the 5G core network.

We can implement this with :   

>def get_core_status():  
    """  
    GET /core  
    Returns the current status of the 5G core network (stopped, starting, running).  
    """  
    pass

-

>def post_core_start():  
    """  
    POST /core/start  
    Starts the 5G core network.  
    """  
    pass

-

>def post_core_restart():  
    """  
    POST /core/restart  
    Restarts the 5G core network.  
    """  
    pass

-

>def post_core_stop():  
    """  
    POST /core/stop  
    Stops the 5G core network.  
    """  
    pass

---

## Next Generation NodeB

This widget shows the status of the next-generation Node B (gNB) and allows users to manage it.

The widget displays the status of the gNB : Stopped, Starting, or Running and also allows the user to Start, Stop, or Restart the gNB.  
It includes :  

- a Configuration button to change the gNB's startup settings,
- a Logs button to view the gNB logs during runtime or compilation,
- a Reset button to reset the gNB configuration file to its default values,  
- and a Compile button to compile the gNB code when it has been modified by the user.

We can implement this with :  

>def post_gnb_start():  
    """  
    POST /gnb/start  
    Starts the gNB service.  
    """  
    pass

-

>def post_gnb_stop():  
    """  
    POST /gnb/stop  
    Stops the gNB service.  
    """  
    pass

-

>def post_gnb_restart():  
    """  
    POST /gnb/restart  
    Restarts the gNB service.  
    """  
    pass

-

>def get_gnb_configuration():  
    """  
    GET /gnb/configuration  
    Returns the current gNB configuration.  
    """  
    pass

-

>def post_gnb_configuration():  
    """  
    POST /gnb/configuration  
    Saves new gNB configuration.  
    """  
    pass

-

>def get_gnb_logs():  
    """  
    GET /gnb/logs  
    Returns logs of the gNB during runtime or compilation.  
    """  
    pass

-

>def post_gnb_reset():  
    """  
    POST /gnb/reset  
    Resets the gNB configuration to default values.  
    """  
    pass

-

>def post_gnb_compile():  
    """  
    POST /gnb/compile  
    Compiles the gNB code.  
    """  
    pass


---

## Overview

This widget shows a quick summary of the network and the throughput.

The widget displays the number of gNBs connected to the 5g core network and UEs, as well as the downlink and uplink data.

We can implement this with :

>def get_summary_gnb():  
    """  
    GET /summery/gnb  
    Returns the list of gNBs connected to the 5G core.  
    """  
    pass

-

>def get_summary_ues():  
    """  
    GET /summery/ues  
    Returns the list of UEs currently attached.  
    """  
    pass

-

>def websocket_downlink():  
    """  
    /ws/downlink  
    WebSocket stream for downlink throughput data.  
    """  
    pass

-

>def websocket_uplink():  
    """  
    /ws/uplink  
    WebSocket stream for uplink throughput data.  
    """  
    pass


---

## Network Status

### Core functions

This widget shows the network status and the connections between each core function.

The widget displays the status between offline, starting and online.

We can implement this with :  

>def get_service_status(service_id: str):  
    """  
    GET /services/{service_id}/status  
    Returns the status of a given core network service.  
    """  
    pass

### External services

#### IP Multimedia subsystem

This widget displays the status of the IMS service, used for handling voice and multimedia communication over IP in 5G networks.

We can implement this with :  

>def get_ims_status():  
    """  
    GET /services/ims/status  
    Returns the status of the IP Multimedia Subsystem (IMS).  
    """  
    pass


#### External Data Network

This widget allows users to test the uplink and downlink throughput between the User Equipment (UE) and the network via the integrated iPerf tool.

We can implement this by integrating the iPerf tool in our project.

To configure the uplink interface, we need an option to allow the user to define the port and the transfer protocol, and a button to initiate the test.

After the initialization we can use iPerf command in a terminal window in the UE:
> iperf -u -t 30 -b 200M -fm -i 1 -c <Server IP>


To make the downlink interface, we need an option to allows the user to define the desired bandwidth, destination IP, port, and transport protocol.

Once the test starts, the widget provides the matching iPerf command to run on the UE.

So we need to make a command generator with a baseline and custom arguments such as bandwidth, destination IP, port, and transport protocol.

After that it will return the perfect iPerf command for the UE.

For our API we can use these paths :  

>def post_edn_uplink_start():  
    """  
    POST /edn/uplink/start  
    Starts the uplink iPerf server on the network.  
    """  
    pass

-

>def post_edn_downlink_start():  
    """  
    POST /edn/downlink/start  
    Starts the downlink iPerf client to test throughput.  
    """  
    pass

-

>def get_edn_status():  
    """  
    GET /edn/status  
    Returns the current status of the EDN interface.  
    """  
    pass

-

>def get_edn_command():  
    """  
    GET /edn/command  
    Returns the iPerf command to be run on the UE with the given parameters.  
    """  
    pass

---

## Radio Access Network

This widget displays the NG-RAN status, indicating whether it is offline, starting, or online.

The widget is also clickable, unlocking a new view that displays the RAN's configuration, detailed information, bitrate, and all connected UEs with their RSSI, downlink and uplink.
NG-RAN's configuration also has buttons to restart, stop, reset, compile and show logs of the NG-RAN and also allows changing the configuration of the Time Division Duplexing (TDD) slot, bandwidth, logical antennas.

We can implement this with :

# RADIO ACCESS NETWORK (RAN)

>def get_ran_status():  
    """  
    GET /ran/status  
    Returns the NG-RAN status (offline, starting, online).  
    """  
    pass

-

>def get_ran_configuration():  
    """  
    GET /ran/configuration  
    Returns the current configuration of the NG-RAN including antennas and TDD slots.  
    """  
    pass

-

>def get_ran_details():  
    """  
    GET /ran/details  
    Returns detailed information about the NG-RAN.  
    """  
    pass

-

>def websocket_ran_bitrate():  
    """  
    /ws/ran/bitrate  
    WebSocket stream of RAN's bitrate data.  
    """  
    pass


---

## User Equipment

This widget displays all users equipment with their status, IMSI and a quick view of their RSSI, RSRP, downlink and uplink.

The IMSI can be retrieved from the SIM card

The widget is also clickable and shows detailed metrics for the selected UE :  
RSSI, RSRP, RSRQ, PHR, SINR, SNR, CQI, MCS, BLER, Bitrate  

We can implement this with :  

>def websocket_ue_metric(ue_id: str, metric: str):  
    """  
    /ws/{ue_id}/{metric}  
    WebSocket stream for UE metrics such as:  
    RSSI, RSRP, RSRQ, PHR, SINR, SNR, CQI, MCS, BLER, Bitrate, uplink, downlink.  
    """  
    pass



Downlink and uplink and all other metrics can be sent also via websocket due to their continuous data :

>def websocket_ue_metric(ue_id: str, metric: str):  
    """  
    /ws/{ue_id}/{metric}  
    WebSocket stream for UE metrics such as:  
    RSSI, RSRP, RSRQ, PHR, SINR, SNR, CQI, MCS, BLER, Bitrate, uplink, downlink.  
    """  
    pass

---

## 5G Standalone Message Flow

This widget provides a visual representation of message flow between core network components and user equipment.

The widget uses Wireshark to analyze packets on the 5G network with a filter, displaying key details including the timestamp, protocol, and a brief summary of each message.

We can implement this widget by capturing packets with TShark. The data can be streamed via WebSocket for live updates, or served using a REST API.


>def websocket_packet_capture():  
    """  
    /ws/pcap  
    WebSocket stream for live packet capture (e.g., TShark or Wireshark data).  
    """  
    pass

-

>def get_packet_capture():  
    """  
    GET /pcap  
    Returns captured packets with timestamps, protocols, and summaries.  
    """  
    pass

---

## Route Table

|   Method   |             Path              |                                    Description                                    |
|:----------:|:-----------------------------:|:---------------------------------------------------------------------------------:|
|    GET     |           /machines           |                           Lists all available machines                            |
|    GET     |         /machine/{id}         |      Retrieves details of a specific machine (name, status, IP, IDs, SDR...)      |
|    POST    |     /machine/{id}/reboot      |                            Reboots a specific machine                             |
|    GET     |             /core             | Retrieves the current status of the 5G core network (stopped, starting, running)  |
|    POST    |          /core/start          |                                Starts the 5G core                                 |
|    POST    |         /core/restart         |                               Restarts the 5G core                                |
|    POST    |          /core/stop           |                                 Stops the 5G core                                 |
|    POST    |          /gnb/start           |                                  Starts the gNB                                   |
|    POST    |           /gnb/stop           |                                   Stops the gNB                                   |
|    POST    |         /gnb/restart          |                                 Restarts the gNB                                  |
|    GET     |      /gnb/configuration       |                      Retrieves the current gNB configuration                      |
|    POST    |      /gnb/configuration       |                           Saves a new gNB configuration                           |
|    GET     |           /gnb/logs           |                     Retrieves gNB logs (runtime/compilation)                      |
|    POST    |          /gnb/reset           |                        Resets gNB configuration to default                        |
|    POST    |         /gnb/compile          |                           Compiles the gNB source code                            |
|    GET     |         /summery/gnb          |                         Lists gNBs connected to the core                          |
|    GET     |         /summery/ues          |                          Lists UEs connected to the core                          |
|    GET     | /services/{service_id}/status |  Retrieves the status of a specific network service (offline, starting, online)   |
|    GET     |     /services/ims/status      |                      Retrieves the status of the IMS service                      |
|    POST    |       /edn/uplink/start       |                    Starts the iPerf server for uplink testing                     |
|    POST    |      /edn/downlink/start      |                  Launches the iPerf client for downlink testing                   |
|    GET     |          /edn/status          |                     Retrieves the status of the EDN interface                     |
|    GET     |         /edn/command          |                   Generates the iPerf command for UE execution                    |
|    GET     |          /ran/status          |                              Retrieves NG-RAN status                              |
|    GET     |      /ran/configuration       |                      Retrieves current NG-RAN configuration                       |
|    GET     |         /ran/details          |                   Retrieves detailed information about the RAN                    |
|    GET     |             /pcap             |                  Retrieves captured packets (Wireshark / TShark)                  |
| WebSocket  |         /ws/downlink          |                      Real-time stream of downlink throughput                      |
| WebSocket  |          /ws/uplink           |                       Real-time stream of uplink throughput                       |
| WebSocket  |        /ws/ran/bitrate        |                        Real-time stream of NG-RAN bitrate                         |
| WebSocket  |     /ws/{ue_id}/{metric}      |    Real-time metric stream for a specific UE (RSSI, RSRP, CQI, Bitrate, etc.)     |
| WebSocket  |           /ws/pcap            |                 Real-time stream of captured packets (Wireshark)                  |