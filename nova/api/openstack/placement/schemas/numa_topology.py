#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""NUMA topology schemas for Placement API."""
import copy

NOVA_NUMA_TOPOLOGY_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer"
            },
            "cpuset": {
                "type": "array"
            },
            "cpu_usage": {
                "type": "integer"
            },
            "memory": {
                "type": "integer"
            },
            "memory_usage": {
                "type": "integer"
            },
            "pinned_cpus": {
                "type": "array"
            },
        },
    },
    "additionalProperties": False,
}

ZUN_NUMA_TOPOLOGY_SCHEMA = copy.deepcopy(NOVA_NUMA_TOPOLOGY_SCHEMA)

PUT_NUMA_TOPOLOGIES_SCHEMA = {
    "type": "object",
    "properties": {
        "uuid": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255,
        },
        "nova_numa_topology": NOVA_NUMA_TOPOLOGY_SCHEMA,
        "zun_numa_topology": ZUN_NUMA_TOPOLOGY_SCHEMA,
    },
    "anyOf": [
        {"required": ["nova_numa_topology"]},
        {"required": ["zun_numa_topology"]}
    ],
    "additionalProperties": False,
}
