# Opentrons-Slack Integration
A simple example showing how to integrate slack messaging as a step of the Opentrons OT2 liquid handling robots.


### Intro
If you are using slack in your organisation you can include a protocol step to send a message to a specific channel. This is useful if you want receive notifications when a protocol is done, or when a specific step needs attention. 

The idea is to take advatange of the python programming of OT2 protocols and introduce a python method that sends a slack message to a predefined channel. In this guide I show a way that does uses the OT2 stock OS, hence is independent of firmware updates (at least in the short term!)


### Setting Up slack to post messages using Incoming Webhooks

The easiest way to programatically send a python message to a slack channel is by defining an incoming webhook. You can read the steps in the official Slack guide [here](https://api.slack.com/messaging/webhooks)

It comes down to 4 steps:
* Create a Slack App   
* Enable Incoming Webhooks
* Create a Webhook. This will provide a URL to send messages to a channel. (You might want to create a dedicated channel for this)
* Send a post request to the webhook with the message


### Sending Post requests using python from the OT2

You can try this out from the command line using cURL

```bash
curl -X POST -H 'Content-type: application/json' --data '{"text":"Help me please! I have been trapped inside this robot!"}'  <YOUR_WEBHOOK_ADDRESS>
```

From python the easiest way of doing it is by importing the Requests Library

```python
import requests

url = <YOUR_WEBHOOK_ADDRESS>
myobj = {'text': 'Help me please! I have been trapped inside this robot!'}

x = requests.post(url, data = myobj)
```
However the requests library is not instaled in the OT2 Raspberry Pi. And since it is running Alpine Linux in a non persistent container, any installation attempt will be deleted when the robot reboots. (There must be a way to either install packages in the persistent "data" folder, or to set up a boot script, but it was outside my knowledge a this point)

One alternative is to use the python built-in urllib module. A post request synthax is slightly less compact that using the request module.


```python
import json
import urllib.request

data = {"text":"Help me please! I have been trapped inside this robot!"}
data = json.dumps(data)

req = urllib.request.Request(url = "<YOUR_WEBHOOK_ADDRESS>", data = bytes(data.encode("utf-8")), method = "POST")

req.add_header("Content-type", "application/json")

with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
```

###  DNS setup on the OT2

If you run the above snippet from your computer, you will most likely post a message into your slack channel succesfully. From the OT2, the snippet will raise an exception:

```bash
URLError: <urlopen error [Errno -3] Temporary failure in name resolution>
```

The root of this issue is a missing DNS configuration.  We can add one from the command line (if you have set up ssh access to your robot)

```bash
echo 'nameserver 8.8.8.8' > /etc/resolv.conf
```

or run directly from a jupyter notebook with the special !() command

```python
!(echo 'nameserver 8.8.8.8' > /etc/resolv.conf)
```
You can verify that the DNS is correctly set by pinging a known website.
```bash
ping www.google.com
```

At this point the python snippet to send post requests should work from the OT2 robot

### Example: Integrating slack messages into a simple protocol

Out of the many ways you can integrate the slack messaging step, here is a simple one that portraits the general idea: a function messageToSlack that takes the message and the channel's webhook as arguments.

```python
SLACK_WEBHOOK= "YOUR_WEBHOOK_ADDRESS"

from opentrons import protocol_api

import json
import urllib.request

def sendMessageToSlack(message,slack_webhook):
    data = {"text":message}
    data = json.dumps(data)

    req = urllib.request.Request(url = slack_webhook, data = bytes(data.encode("utf-8")), method = "POST")

    req.add_header("Content-type", "application/json")

    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode())
        
        
metadata = {'apiLevel': '2.2'}

def run(protocol: protocol_api.ProtocolContext):
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_1])

    p300.transfer(100, plate['A1'], plate['B1'])
    
    sendMessageToSlack("Help, I am trapped inside this robot!", SLACK_WEBHOOK)
    
    p300.transfer(100, plate['B1'], plate['A1'])
    
    sendMessageToSlack("Please! Somebody! Help me!!!", SLACK_WEBHOOK)
``` 

You can run this from the OT2's jupyter notebook server, or embedded it into your protocol python file and upload it via the Opentrons APP. You may want to add an initialization block that writes the DNS address for the cases where the robot has been rebooted. 

