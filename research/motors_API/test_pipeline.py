"""
Test script to run the complete pipeline from the notebook.
"""
import os
import sys
import json
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import base64
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import requests

# Load environment variables
from dotenv import load_dotenv
import os as os_module
creds_path = os_module.path.join(os_module.path.dirname(__file__), '..', 'creds', '.env')
load_dotenv(creds_path)

# Authentication variables
PUBLIC_KEY = os.environ.get('C_PUBLIC_KEY')
PRIVATE_KEY = os.environ.get('C_PRIVATE_KEY')
BASE_URL = 'https://api.edmunds.com'

# Test VIN
TEST_VIN = "3FA6P0D9XLR115438"

def GenerateSharedAuth(d: datetime, public_key: str, private_key: str, uri: str, body: str = "") -> str:
    """Generate HMAC-SHA256 authentication header."""
    auth_string = uri + str(int(d.timestamp()))

    if body:
        body_md5 = base64.b64encode(hashlib.md5(body.encode()).digest()).decode()
        auth_string += body_md5

    signature = base64.b64encode(
        hmac.new(private_key.encode(), auth_string.encode(), hashlib.sha256).digest()
    ).decode()

    return f"SharedKey {public_key}:{signature}"

def GetResponse(uri: str) -> str:
    """Make authenticated API request and return response body."""
    now = datetime.now(timezone.utc)
    auth_header = GenerateSharedAuth(now, PUBLIC_KEY, PRIVATE_KEY, uri)

    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/xml"
    }

    full_url = BASE_URL + uri
    print(f"  [API] GET {uri[:80]}...")

    response = requests.get(full_url, headers=headers)
    response.raise_for_status()

    return response.text

def strip_ns(tag):
    """Remove XML namespace from tag."""
    return tag.split('}')[-1] if '}' in tag else tag

def parse_vehicle_search(xml_string: str) -> Dict:
    """Parse vehicle search response."""
    root = ET.fromstring(xml_string)

    vehicles = []
    for elem in root.iter():
        if strip_ns(elem.tag) == 'Vehicle':
            vehicle = {}
            for child in elem:
                tag = strip_ns(child.tag)
                if child.text:
                    vehicle[tag] = child.text
            vehicles.append(vehicle)

    return {
        'vehicles': vehicles,
        'base_vehicle_id': vehicles[0].get('id') if vehicles else None
    }

# Now run the steps
print(f"Testing with VIN: {TEST_VIN}\n")

# STEP 1
print("STEP 1: Vehicle lookup...")
try:
    resp = GetResponse(f"/v1/Information/Vehicles/Search/ByVIN?vin={TEST_VIN}")
    vehicle_data = parse_vehicle_search(resp)
    print(f"OK: Vehicle found: {vehicle_data['vehicles'][0].get('year')} {vehicle_data['vehicles'][0].get('make')} {vehicle_data['vehicles'][0].get('model')}\n")
except Exception as e:
    print(f"ERROR in STEP 1: {e}")
    sys.exit(1)

# STEP 2
print("STEP 2: Get work-time summaries...")
try:
    vehicle_id = vehicle_data["vehicles"][0].get('id')
    print(f"  Vehicle ID: {vehicle_id}")

    resp = GetResponse(
        f"/v1/Information/Vehicles/Attributes/BaseVehicleId/{vehicle_id}"
        f"/Content/Summaries/Of/EstimatedWorkTimes/?systemID=5&groupID=&subGroupID="
    )

    # Extract application IDs
    root = ET.fromstring(resp)
    app_ids = []
    for elem in root.iter():
        if strip_ns(elem.tag) == 'EstimatedWorkTimeApplicationSummary':
            for child in elem:
                if strip_ns(child.tag) == 'ApplicationID' and child.text:
                    app_ids.append(child.text)
                    break

    print(f"OK: Found {len(app_ids)} work-time applications\n")
except Exception as e:
    print(f"ERROR in STEP 2: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nBasic API connectivity test PASSED!")
print(f"Successfully connected to Motors API and retrieved data for VIN: {TEST_VIN}")
