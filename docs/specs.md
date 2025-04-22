# Specification

## Route Table

|   Method    |                          Path                          |                   Description                    |
|:-----------:|:------------------------------------------------------:|:------------------------------------------------:|
|    `GET`    |              [`/machines`](#get-machines)              |    Lists all available machines with their id    |
|    `GET`    |     [`/machine/{id}/status`](#get-machineidstatus)     |             Retrieves machine status             |
|    `GET`    |  [`/machine/{id}/client_id`](#get-machineidclient_id)  |             Retrieves the client id              |
|    `GET`    | [`/machine/{id}/machine_id`](#get-machineidmachine_id) |             Retrieves the machine id             |
|    `GET`    |        [`/machine/{id}/sdr`](#get-machineidsdr)        |            Retrieves the machine sdr             |
|    `GET`    |         [`/machine/{id}/ip`](#get-machineidip)         |             Retrieves the machine ip             |
|   `POST`    |    [`/machine/{id}/reboot`](#post-machineidreboot)     |            Reboots a specific machine            |
|    `GET`    |           [`/core/status`](#get-corestatus)            |   Retrieves the status of the 5G core network    |
|   `POST`    |            [`/core/start`](#post-corestart)            |                Starts the 5G core                |
|   `POST`    |          [`/core/restart`](#post-corerestart)          |               Restarts the 5G core               |
|   `POST`    |             [`/core/stop`](#post-corestop)             |                Stops the 5G core                 |
|   `POST`    |             [`/gnb/start`](#post-gnbstart)             |                  Starts the gNB                  |
|   `POST`    |              [`/gnb/stop`](#post-gnbstop)              |                  Stops the gNB                   |
|   `POST`    |           [`/gnb/restart`](#post-gnbrestart)           |                 Restarts the gNB                 |
|    `GET`    |     [`/gnb/configuration`](#get-gnbconfiguration)      |     Retrieves the current gNB configuration      |
|   `POST`    |     [`/gnb/configuration`](#post-gnbconfiguration)     |          Saves a new gNB configuration           |
| `Websocket` |         [`/ws/gnb/logs`](#websocket-wsgnblogs)         |     Retrieves gNB logs (runtime/compilation)     |
|   `POST`    |             [`/gnb/reset`](#post-gnbreset)             |       Resets gNB configuration to default        |
|   `POST`    |           [`/gnb/compile`](#post-gnbcompile)           |           Compiles the gNB source code           |
|    `GET`    |           [`/summary/gnb`](#get-summarygnb)            |         Lists gNBs connected to the core         |
|    `GET`    |            [`/summary/ue`](#get-summaryue)             |         Lists UEs connected to the core          |
|    `GET`    |   [`/services/nssf/status`](#get-servicesnssfstatus)   |            Retrieves the NSSF status             |
|    `GET`    |   [`/services/ausf/status`](#get-servicesausfstatus)   |            Retrieves the AUSF status             |
|    `GET`    |    [`/services/nrf/status`](#get-servicesnrfstatus)    |             Retrieves the NRF status             |
|    `GET`    |    [`/services/smf/status`](#get-servicessmfstatus)    |             Retrieves the SMF status             |
|    `GET`    |    [`/services/udr/status`](#get-servicesudrstatus)    |             Retrieves the UDR status             |
|    `GET`    |    [`/services/upf/status`](#get-servicesupfstatus)    |             Retrieves the UPF status             |
|    `GET`    |    [`/services/amf/status`](#get-servicesamfstatus)    |             Retrieves the AMF status             |
|    `GET`    |    [`/services/udm/status`](#get-servicesudmstatus)    |             Retrieves the UDM status             |
|    `GET`    |    [`/services/ims/status`](#get-servicesimsstatus)    |     Retrieves the status of the IMS service      |
|   `POST`    |      [`/edn/uplink/start`](#post-ednuplinkstart)       |    Starts the iPerf server for uplink testing    |
|   `POST`    |    [`/edn/downlink/start`](#post-edndownlinkstart)     |  Launches the iPerf client for downlink testing  |
|    `GET`    |            [`/edn/status`](#get-ednstatus)             |    Retrieves the status of the EDN interface     |
|    `GET`    |           [`/edn/command`](#get-edncommand)            |   Generates the iPerf command for UE execution   |
|    `GET`    |            [`/ran/status`](#get-ranstatus)             |               Retrieves RAN status               |
|    `GET`    |     [`/ran/configuration`](#get-ranconfiguration)      |       Retrieves current RAN configuration        |
|    `GET`    |                  [`/pcap`](#get-pcap)                  | Retrieves captured packets (Wireshark / TShark)  |
| `Websocket` |     [`/ws/avgdownlink`](#websocket-wsavgdownlink)      | Real-time average stream of downlink throughput  |
| `Websocket` |       [`/ws/avguplink`](#websocket-wsavguplink)        |  Real-time average stream of uplink throughput   |
| `Websocket` |      [`/ws/ran/bitrate`](#websocket-wsranbitrate)      |         Real-time stream of RAN bitrate          |
| `Websocket` |   [`/ws/{ue_id}/{metric}`](#websocket-wsue_idmetric)   |    Real-time stream for a specific UE metric     |
| `Websocket` |            [`/ws/pcap`](#websocket-wspcap)             | Real-time stream of captured packets (Wireshark) |


## Machine Selector

We would like to define a widget, `widget_machines_selector`, allow the user to select which machines to monitor and control.

The `widget_machines_selector` should display the selected machine name and, when clicked, expand to reveal all available machines.

### Machine selector Routes detailed


###### GET `/machines`

```python  
def get_machines():  
    """  
    GET /machines  
    Returns a list of all available machines with their names and ID.  
    """  
    pass
```

---

## Machine Information

We would like to define a widget, `widget_machine_info`, containing data about the machine.

`widget_machine_info` should contain the following information :

- The machine status, either offline or online.
- The unique client id.
- The unique machine id.
- The Software Defined Radio Device being used.
- The locally assigned IP address.
- The reboot button.

### Machine information Routes detailed

###### GET  `/machine/{id}/status`
```python 
def get_machine_status(id: str):
    """ 
    GET /machine/{id}/status
    Returns the current status of the selected machine.
    """ 
    pass
```

###### GET `/machine/{id}/client_id`
```python 
def get_machine_client_id(id: str):
    """
    GET /machine/{id}/client_id
    Returns the unique client ID.
    """
    pass
```

###### GET `/machine/{id}/machine_id`
```python 
def get_machine_machine_id(id: str):
    """
    GET /machine/{id}/machine_id
    Returns the machine ID of the selected machine.
    """
    pass
```

###### GET `/machine/{id}/sdr`
```python 
def get_machine_sdr(id: str):
    """
    GET /machine/{id}/sdr
    Returns the SDR device associated with the selected machine.
    """
    pass
```

###### GET `/machine/{id}/ip`
```python 
def get_machine_ip(id: str):
    """
    GET /machine/{id}/ip
    Returns the IP address of the selected machine.
    """
    pass
```

###### POST `/machine/{id}/reboot`
```python 
def post_machine_reboot(id: str):  
    """  
    POST /machine/{id}/reboot  
    Triggers a reboot of the selected machine.  
    """  
    pass
```

---

## 5G Core Network

We would like to define a widget, `widget_5GCN`, containing data and action button about the 5G Core Network.

`widget_5GCN `should contain the following information :

- The 5G Core Network status either stopped, starting, running or upgrading.
- An action button that stops the 5G Core Network when it is running.
- An action button that start the 5G Core Network and when he is running replaced by a restart button.

### 5G Core Network Routes detailed

###### GET `/core/status`
```python 
def get_core_status():        
    """  
    GET /core/status
    Returns the current status of the 5G core network (stopped, starting, running, upgrading).  
    """  
    pass
```

###### POST `/core/start`
```python 
def post_core_start():  
    """  
    POST /core/start  
    Starts the 5G core network.  
    """  
    pass
```

###### POST `/core/restart`
```python 
def post_core_restart():  
    """  
    POST /core/restart  
    Restarts the 5G core network.  
    """  
    pass
```

###### POST `/core/stop`
```python 
def post_core_stop():  
    """  
    POST /core/stop  
    Stops the 5G core network.  
    """  
    pass
```

---

## Next Generation NodeB

We would like to define a widget, `widget_gNB`, containing data and action button about the Next Generation NodeB (gNB).

`widget_gNB` should contain the following information :

- The gNB status either stopped, starting, running, compiling or upgrading.
- An action button starts the gNB and when it is running is replaced by stop and restart buttons.
- A Configuration button allows the user to change the gNB startup settings.
- A Logs button lets the user view the gNB logs during runtime or compilation.
- A Reset button resets the gNB configuration file to its default values.
- A Compile button compiles the gNB code if it has been modified by the user.

### Next Generation NodeB Routes detailed

###### POST `/gnb/start`
```python 
def post_gnb_start():  
    """  
    POST /gnb/start  
    Starts the gNB service.  
    """  
    pass
```

###### POST `/gnb/stop`
```python 
def post_gnb_stop():  
    """  
    POST /gnb/stop  
    Stops the gNB service.  
    """  
    pass
```

###### POST `/gnb/restart`
```python 
def post_gnb_restart():  
    """  
    POST /gnb/restart  
    Restarts the gNB service.  
    """  
    pass
```

###### GET `/gnb/configuration`
```python 
def get_gnb_configuration():  
    """  
    GET /gnb/configuration  
    Returns the current gNB configuration.  
    """  
    pass
```

###### POST `/gnb/configuration`
```python 
def post_gnb_configuration():  
    """  
    POST /gnb/configuration  
    Saves new gNB configuration.  
    """  
    pass
```

###### Websocket `/ws/gnb/logs`
```python 
def get_gnb_logs():  
    """  
    /ws/gnb/logs  
    Websocket stream logs of the gNB during runtime or compilation.  
    """  
    pass
```

###### POST `/gnb/reset`
```python 
def post_gnb_reset():  
    """  
    POST /gnb/reset  
    Resets the gNB configuration to default values.  
    """  
    pass
```

###### POST `/gnb/compile`
```python 
def post_gnb_compile():  
    """  
    POST /gnb/compile  
    Compiles the gNB code.  
    """  
    pass
```

---

## Summary of the Network

We would like to define a widget, `widget_summary_network`, containing data about the Network.

`widget_summary_network` should contain the following information :

- The number of gNBs connected to the 5G Core Network.
- The number of User Equipment (UE) attached.
- The real-time downlink throughput.
- The real-time uplink throughput.

### Summary of the Network Routes detailed

###### GET `/summary/gnb`
```python
def get_summary_gnb():  
    """  
    GET /summary/gnb  
    Returns the list of gNBs connected to the 5G core.  
    """  
    pass
```

###### GET `/summary/ue`
```python
def get_summary_ues():  
    """  
    GET /summary/ue
    Returns the list of UEs currently attached.  
    """  
    pass
```

###### Websocket `/ws/avgdownlink`
```python
def avg_throughput_downlink():
    """  
    /ws/avgdownlink  
    WebSocket stream for downlink throughput data.  
    """  
    pass
```

###### Websocket `/ws/avguplink`
```python
def avg_throughput_uplink():  
    """  
    /ws/avguplink  
    WebSocket stream for uplink throughput data.  
    """  
    pass
```

---

## Network Status

### Core functions

We would like to define a widget, `widget_core_status`, containing data about the Core functions.

`widget_core_status` should contain the following information :

- The status of all Core functions is either offline, starting or online.

### Network Status Routes detailed

###### GET `/services/nssf/status`
```python 
def get_nssf_status():  
    """  
    GET /services/nssf/status  
    Returns the NSSF status.  
    """  
    pass
```

###### GET `/services/ausf/status`
```python 
def get_ausf_status():  
    """  
    GET /services/ausf/status  
    Returns the AUSF status.  
    """  
    pass
```

###### GET `/services/nrf/status`
```python 
def get_nrf_status():  
    """  
    GET /services/nrf/status  
    Returns the NRF status.  
    """  
    pass
```

###### GET `/services/smf/status`
```python 
def get_smf_status():  
    """  
    GET /services/smf/status  
    Returns the SMF status.  
    """  
    pass
```

###### GET `/services/udr/status`
```python 
def get_udr_status():  
    """  
    GET /services/udr/status  
    Returns the UDR status.  
    """  
    pass
```

###### GET `/services/upf/status`
```python 
def get_upf_status():  
    """  
    GET /services/upf/status  
    Returns the UPF status.  
    """  
    pass
```

###### GET `/services/amf/status`
```python 
def get_amf_status():  
    """  
    GET /services/amf/status  
    Returns the AMF status.  
    """  
    pass
```

###### GET `/services/udm/status`
```python 
def get_udm_status():  
    """  
    GET /services/udm/status  
    Returns the UDM status.  
    """  
    pass
```

### External services

#### IP Multimedia subsystem

We would like to define a widget, `widget_IMS`, containing data about the Ip Multimedia Subsystem (IMS).

`widget_IMS`, should contain the following information :

- The IMS status should be either offline or online.

### IMS Routes detailed

###### GET `/services/ims/status`
```python 
def get_ims_status():  
    """  
    GET /services/ims/status  
    Returns the status of the IP Multimedia Subsystem (IMS).  
    """  
    pass
```

#### External Data Network (EDN)

This widget allows users to test the uplink and downlink throughput between the User Equipment (UE) and the network via the integrated iPerf tool.

We can implement this by integrating the iPerf tool in our project.

To configure the uplink interface, we need an option to allow the user to define the port and the transfer protocol, and a button to initiate the test.

After initialization, the iPerf command can be used in a UE terminal window :
```
iperf -u -t 30 -b 200M -fm -i 1 -c <Server IP>
```

To make the downlink interface, we need an option to allow the user to define the desired bandwidth, destination IP, port, and transport protocol.

Once the test starts, the widget provides the matching iPerf command to run on the UE.

So we need to make a command generator with a baseline and custom arguments such as bandwidth, destination IP, port, and transport protocol.

After that it will return the perfect iPerf command for the UE.

### EDN Routes detailed 

###### POST `/edn/uplink/start`
```python
def post_edn_uplink_start():  
    """  
    POST /edn/uplink/start  
    Starts the uplink iPerf server on the network.  
    """  
    pass
```

###### POST `/edn/downlink/start`
```python
def post_edn_downlink_start():  
    """  
    POST /edn/downlink/start  
    Starts the downlink iPerf client to test throughput.  
    """  
    pass
```

###### GET `/edn/status `
```python
def get_edn_status():  
    """  
    GET /edn/status  
    Returns the current status of the EDN interface.  
    """  
    pass
```

###### GET `/edn/command `
```python
def get_edn_command():  
    """  
    GET /edn/command  
    Returns the iPerf command to be run on the UE with the given parameters.  
    """  
    pass
```

---

## Radio Access Network

We would like to define a widget, `widget_RAN`, containing data about the Radio Access Network (RAN).

`widget_RAN` should contain the following information :

- The gNodeB status, either offline, starting, or online.
- The gNodeB configuration ( TDD, bandwidth, ...)
- The gNodeB current configuration and some static metrics.
- The gNodeB radio metrics ( RSSI, SINR, ...)

### RAN Routes detailed

###### GET `/ran/status`
```python
def get_ran_status():  
    """  
    GET /ran/status  
    Returns the RAN status (offline, starting, online).  
    """  
    pass
```

###### GET `/ran/configuration`
```python
def get_ran_configuration():  
    """  
    GET /ran/configuration  
    Returns the current configuration of the RAN including antennas and TDD slots.  
    """  
    pass
```

###### Websocket `/ws/ran/bitrate  `
```python
def websocket_ran_bitrate():  
    """  
    /ws/ran/bitrate  
    WebSocket stream of RAN's bitrate data.  
    """  
    pass
```

---

## User Equipment

We would like to define a widget, `widget_UE`, containing data about the User Equipment (UE).

`widget_UE` should contain the following information :

- The list of User Equipment
- User Equipment metrics (IMSI, RSSI, RSRP, Uplink and Downlink)
- When clicked show all radio metrics (Rssi, SINR, ...)

### User Equipment Routes detailed

###### Websocket `/ws/{ue_id}/{metric}`
```python
def websocket_ue_metric(ue_id: str, metric: str):  
    """  
    /ws/{ue_id}/{metric}  
    WebSocket stream for UE metrics such as:  
    RSSI, RSRP, RSRQ, PHR, SINR, SNR, CQI, MCS, BLER, Bitrate, uplink, downlink.  
    """  
    pass
```

---

## Message Flow / Wireshark View

We would like to define a widget, `widget_tshark_view`, containing data about packet on the 5G network with a filter.

`widget_tshark_view` should contain the following information :

- Time of the packet.
- Protocol of the packet.
- Summary of the message content of the packet.


We can implement this widget by capturing packets with TShark. The data can be streamed via WebSocket for live updates, or served using a REST API.

###### Websocket `/ws/pcap`
```python
def websocket_packet_capture():  
    """  
    /ws/pcap  
    WebSocket stream for live packet capture (TShark).  
    """  
    pass
```

###### GET `/pcap`
```python
def get_packet_capture():  
    """  
    GET /pcap  
    Returns captured packets with timestamps, protocols, and summaries.  
    """  
    pass
```
