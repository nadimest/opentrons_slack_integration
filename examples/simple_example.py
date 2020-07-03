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
