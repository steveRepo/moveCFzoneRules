# WORK IN PROGRESS

import json
import requests

AUTH_KEY = "<>"
AUTH_EMAIL = "<>"

class LoadBalancer:
    def __init__(self, lb_data):
        self.lb_data = lb_data
        self.id = lb_data["id"]
        self.name = lb_data["name"]

class Pool:
    def __init__(self, pool_data):
        self.pool_data = pool_data
        self.id = pool_data["id"]
        self.name = pool_data["name"]

class Monitor:
    def __init__(self, monitor_data):
        self.monitor_data = monitor_data
        self.id = monitor_data["id"]
        self.name = monitor_data["name"]

def fetch_pools():
    url = "https://api.cloudflare.com/client/v4/user/load_balancers/pools"
    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"Error retrieving pool list. Status code: {response.status_code}")
        print(response.content)
        exit(1)

    pool_list = response.json()["result"]
    pools = []
    for pool_data in pool_list:
        pool = Pool(pool_data)
        pools.append(pool)
    return pools

def fetch_monitors():
    url = "https://api.cloudflare.com/client/v4/user/load_balancers/monitors"
    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"Error retrieving monitor list. Status code: {response.status_code}")
        print(response.content)
        exit(1)

    monitor_list = response.json()["result"]
    monitors = []
    for monitor_data in monitor_list:
        monitor = Monitor(monitor_data)
        monitors.append(monitor)
    return monitors

def fetch_load_balancers(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/load_balancers"
    response = requests.get(
        url,
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"Error retrieving load balancer list. Status code: {response.status_code}")
        print(response.content)
        exit(1)

    lb_list = response.json()["result"]
    load_balancers = []
    for lb_data in lb_list:
        load_balancer = LoadBalancer(lb_data)
        load_balancers.append(load_balancer)
    return load_balancers

def get_fallback_pool_id(pools):
    for pool in pools:
        if pool.name == "fallback pool":
            return pool.id
    return None

def get_http_monitor_id(monitors):
    for monitor in monitors:
        if monitor.name == "http monitor":
            return monitor.id
    return None

def create_pool_on_target(pool_data, target_zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{target_zone_id}/load_balancers/pools"

    response = requests.post(
        url,
        json=pool_data,
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"> - Pool '{pool_data['name']}' not created. Status code: {response.status_code}")
        print(response.content)
        return None

    pool_data = response.json()["result"]
    pool = Pool(pool_data)

    print(f"> + Pool '{pool.name}' created successfully in the target zone.")
    return pool.id

def create_monitor_on_target(monitor_data, target_zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{target_zone_id}/load_balancers/monitors"

    response = requests.post(
        url,
        json=monitor_data,
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"> - Monitor '{monitor_data['name']}' not created. Status code: {response.status_code}")
        print(response.content)
        return None

    monitor_data = response.json()["result"]
    monitor = Monitor(monitor_data)

    print(f"> + Monitor '{monitor.name}' created successfully in the target zone.")
    return monitor.id

def get_fallback_pool_id(pools):
    for pool in pools:
        if pool.name == "fallback pool":
            return pool.id
    return None

def get_http_monitor_id(monitors):
    for monitor in monitors:
        if monitor.name == "http monitor":
            return monitor.id
    return None

def create_load_balancer_on_target(lb, target_zone_id, pools, monitors):
    lb_data = lb.lb_data
    lb_name = lb.name

    if "id" in lb_data:
        del lb_data["id"]
    if "created_on" in lb_data:
        del lb_data["created_on"]
    if "modified_on" in lb_data:
        del lb_data["modified_on"]
    if "probe_modified_on" in lb_data:
        del lb_data["probe_modified_on"]

    # Create the fallback pool if it doesn't exist
    fallback_pool_id = get_fallback_pool_id(pools)
    if fallback_pool_id is None:
        fallback_pool_data = {"name": "fallback pool", "enabled": True}
        fallback_pool_id = create_pool_on_target(fallback_pool_data, target_zone_id)
        pools.append(Pool({"id": fallback_pool_id, "name": "fallback pool"}))

    # Create the HTTP monitor if it doesn't exist
    http_monitor_id = get_http_monitor_id(monitors)
    if http_monitor_id is None:
        http_monitor_data = {"name": "http monitor", "type": "http", "method": "GET", "path": "/", "expected_codes": "2xx"}
        http_monitor_id = create_monitor_on_target(http_monitor_data, target_zone_id)
        monitors.append(Monitor({"id": http_monitor_id, "name": "http monitor"}))

    # Add the fallback pool and HTTP monitor IDs to the load balancer data
    lb_data["fallback_pool"] = fallback_pool_id
    lb_data["monitor"] = {"type": "http", "id": http_monitor_id}

    url = f"https://api.cloudflare.com/client/v4/zones/{target_zone_id}/load_balancers"

    response = requests.post(
        url,
        json=lb_data,
        params={"name": lb_name},
        headers={"Content-Type": "application/json", "X-Auth-Key": f"{AUTH_KEY}", "X-Auth-Email": f"{AUTH_EMAIL}"}
    )

    if response.status_code != 200:
        print(f"> - Load balancer '{lb_name}' not created. Status code: {response.status_code}")
        print(response.content)
        return

    lb_data = response.json()["result"]
    lb = LoadBalancer(lb_data)

    print(f"> + Load balancer '{lb_name}' created successfully in the target zone.")


if __name__ == "__main__":
    source_zone_id = input("Enter source zone ID: ")
    target_zone_id = input("Enter target zone ID: ")

    print("Fetching load balancers...")
    load_balancers = fetch_load_balancers(source_zone_id)

    print("Fetching pools...")
    pools = fetch_pools()

    print("Fetching monitors...")
    monitors = fetch_monitors()

    print(f"Found {len(load_balancers)} load balancers in the source zone.")

    for lb in load_balancers:
        print(f"Creating load balancer '{lb.name}' in the target zone...")
        create_load_balancer_on_target(lb, target_zone_id, pools, monitors)








