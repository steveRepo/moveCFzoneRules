# This script Deletes Zone Rulesets from a target zone.
# Add your Auth below before use

# To use, ensure you have python installed (https://docs.brew.sh/Homebrew-and-Python).
# To run: $ python ruleset-transfer.py 
# Script prompts for the target zone.


import json
import requests

AUTH_KEY = "<auth_key>"
AUTH_EMAIL = "<auth-email>"

class Ruleset:
    def __init__(self, ruleset_data):
        self.ruleset_data = ruleset_data
        self.key = f"{self.ruleset_data['phase']}_{self.ruleset_data['name']}"

def fetch_rulesets(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    rulesets = []

    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"Error retrieving rulesets. Status code: {response.status_code}")
        print(response.content)
        exit(1)

    raw_rulesets = response.json()["result"]
    print(f"Retrieved rulesets for zone {zone_id}")

    for raw_ruleset in raw_rulesets:
        ruleset_id = raw_ruleset["id"]
        ruleset_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{ruleset_id}"
        response = requests.get(
            ruleset_url,
            headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
        )

        if response.status_code != 200:
            print(f"Error retrieving ruleset details. Status code: {response.status_code}")
            print(response.content)
            exit(1)

        ruleset_details = response.json()["result"]

        if "version" in ruleset_details:
            del ruleset_details["version"]
        if "last_updated" in ruleset_details:
            del ruleset_details["last_updated"]
        if "rules" in ruleset_details:
            for rule in ruleset_details["rules"]:
                if "id" in rule:
                    del rule["id"]

        rulesets.append(Ruleset(ruleset_details))

    return rulesets

def delete_target_rulesets(target_rulesets, target_zone_id):
    for ruleset in target_rulesets:
        ruleset_id = ruleset.ruleset_data["id"]
        url = f"https://api.cloudflare.com/client/v4/zones/{target_zone_id}/rulesets/{ruleset_id}"

        response = requests.delete(
            url,
            headers={"Content-Type": "application/json", "X-Auth-Key": AUTH_KEY, "X-Auth-Email": AUTH_EMAIL}
        )

        if response.status_code != 200:
            continue  # Skip to the next ruleset in case of an error

        print(f"> Ruleset with ID '{ruleset_id}' successfully deleted from target zone.")
    

target_zone = input("Enter the target zone ID to delete ruleset: ")

target_rulesets = fetch_rulesets(target_zone)
delete_target_rulesets(target_rulesets, target_zone)


print("Ruleset deletion Complete.")