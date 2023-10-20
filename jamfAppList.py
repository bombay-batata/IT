import os
import shutil

import requests
import xmltodict
import csv

# Set your Jamf Pro server URL and API credentials
JSS_URL = "https://XXX.jamfcloud.com"
API_USER = JAMF_USER
API_PASS = JAMF_TOKEN

# Create a temporary directory to store the application inventory
temp_dir = "/tmp"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Get a list of all computer IDs
all_comp_ids = []
response = requests.get(
    f"{JSS_URL}/JSSResource/computers",
    auth=(API_USER, API_PASS),
    headers={"Accept": "application/xml"},
)
computer_id_counter = 0
for computer in xmltodict.parse(response.content.decode("utf-8"))["computers"]["computer"]:
    all_comp_ids.append(computer["id"])
    computer_id_counter = computer_id_counter + 1
#test
print(computer_id_counter)
print(all_comp_ids)

# Iterate over all computer IDs and get the application inventory for each computer
#test
#computer_name_counter = 0
for comp_id in all_comp_ids:
    # Get the computer name

    computer_name = xmltodict.parse(
        requests.get(
            f"{JSS_URL}/JSSResource/computers/id/{comp_id}",
            auth=(API_USER, API_PASS),
            headers={"Accept": "application/xml"},
        ).content.decode("utf-8")
    )["computer"]["general"]["name"]
    #test
    # computer_name_counter = computer_name_counter + 1
    # print(computer_name_counter)
    # Get the macOS version
    os_version = xmltodict.parse(
        requests.get(
            f"{JSS_URL}/JSSResource/computers/id/{comp_id}",
            auth=(API_USER, API_PASS),
            headers={"Accept": "application/xml"},
        ).content.decode("utf-8")
    )["computer"]["hardware"]["os_version"]
    #test
    #print(os_version)

    # Get the list of applications installed on the computer
    response = requests.get(
        f"{JSS_URL}/JSSResource/computers/id/{comp_id}",
        auth=(API_USER, API_PASS),
        headers={"Accept": "application/xml"},
    )

    # Parse the XML response to get the list of applications
    try:
        applications = xmltodict.parse(response.content.decode("utf-8"))["computer"]["software"]["applications"]["application"]
    except KeyError:
        applications = []



    #test
    print(applications)

    # Create a CSV file for the computer's application inventory
    with open(os.path.join(temp_dir, f"{computer_name}.csv"), "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Computer Name", "macOS Version", "Application Name", "Application Version"])
        for application in applications:
            writer.writerow([computer_name, os_version, application["name"], application["version"].strip()])


# Combine all of the individual application inventory CSV files into a single file
with open("AllMacAppInventory.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Computer Name", "macOS Version", "Application Name", "Application Version"])
    for filename in os.listdir(temp_dir):
        if filename.endswith(".csv"):
            with open(os.path.join(temp_dir, filename), "r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    writer.writerow(row)

# # Remove the temporary directory
shutil.rmtree(temp_dir)
