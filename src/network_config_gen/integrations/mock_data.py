"""Mock data for testing and development."""

from typing import Any, Dict, List


def get_mock_devices() -> List[Dict[str, Any]]:
    """Return mock device data from ServiceNow."""
    return [
        {
            "sys_id": "mock-001",
            "name": "switch-core-01",
            "manufacturer": "cisco",
            "os": "ios-xe",
            "model": "c9300-24uxm",
            "serial_number": "JAE12345678901",
            "hardware_status": "in use",
            "ip_address": "10.0.0.1",
            "location": "datacenter-1",
            "config": {
                "role": "core",
                "vlans": ["1", "100", "200", "300"],
                "bgp_asn": "65001",
            },
        },
        {
            "sys_id": "mock-002",
            "name": "switch-access-01",
            "manufacturer": "arista",
            "os": "eos",
            "model": "dcs-7050s3",
            "serial_number": "JPE98765432101",
            "hardware_status": "in use",
            "ip_address": "10.0.0.2",
            "location": "datacenter-1",
            "config": {
                "role": "access",
                "vlans": ["1", "100", "200"],
                "spanning_tree": "rapid-pvst",
            },
        },
        {
            "sys_id": "mock-003",
            "name": "switch-edge-01",
            "manufacturer": "juniper",
            "os": "junos",
            "model": "ex4650",
            "serial_number": "JN1234567890AB",
            "hardware_status": "planned",
            "ip_address": "10.0.0.3",
            "location": "branch-1",
            "config": {
                "role": "edge",
                "vlans": ["1", "100"],
                "mpls_enabled": True,
            },
        },
    ]


def get_mock_secrets() -> Dict[str, Dict[str, str]]:
    """Return mock secrets for devices."""
    return {
        "switch-core-01": {
            "username": "admin",
            "password": "C0reP@ssw0rd!",
            "enable_password": "EnableP@ss123",
        },
        "switch-access-01": {
            "username": "netadmin",
            "password": "Acc3ssP@ss!",
            "api_key": "eapi-key-12345",
        },
        "switch-edge-01": {
            "username": "admin",
            "password": "EdgeP@ssw0rd!",
            "snmp_community": "public-ro",
        },
    }
