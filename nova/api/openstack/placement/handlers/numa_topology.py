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
"""Placement API handlers for NUMA topology information."""

from oslo_utils import encodeutils
import json
import jsonschema
import webob

from nova.api.openstack.placement import errors
from nova.api.openstack.placement import exception
from nova.api.openstack.placement import microversion
from nova.api.openstack.placement.objects import resource_provider as rp_obj
from nova.api.openstack.placement.policies import numa_topology as policies
from nova.api.openstack.placement.schemas import numa_topology as schema
from nova.api.openstack.placement import util
from nova.api.openstack.placement import wsgi_wrapper
from nova.i18n import _


@wsgi_wrapper.PlacementWsgify
@util.check_accept('application/json')
def get_numa_topologies_for_resource_provider(req):
    """GET a dictionary of resource provider NUMA topology by resource class.

    If the resource provider does not exist return a 404.

    On success return a 200 with an application/json representation of
    the NUMA topology dictionary.
    """
    context = req.environ['placement.context']
    context.can(policies.SHOW)
    # want_version = req.environ[microversion.MICROVERSION_ENVIRON]
    uuid = util.wsgi_path_item(req.environ, 'uuid')
    response = req.response
    numa_topology = rp_obj.NUMATopology.get_by_resource_provider_uuid(context,
                                                                      uuid)
    # print('numa_topology', numa_topology)
    if numa_topology.nova_numa_topology is not None:
        nova_numa_topology = json.loads(numa_topology.nova_numa_topology)
    else:
        nova_numa_topology = None
    if numa_topology.zun_numa_topology is not None:
        zun_numa_topology = json.loads(numa_topology.zun_numa_topology)
    else:
        zun_numa_topology = None
    # print('loads_nova_numa_topology_from_db', nova_numa_topology)
    # print('loads_zun_numa_topology_from_db', zun_numa_topology)
    total_numa_topologies = []
    if nova_numa_topology is not None and zun_numa_topology is not None:
        for cell in nova_numa_topology['nova_numa_topology']:
            for node in zun_numa_topology['zun_numa_topology']:
                if cell['id'] == node['id']:
                    total_cpu_usage = cell['cpu_usage'] + node['cpu_usage']
                    total_pinned_cpus = cell['pinned_cpus'] + node[
                        'pinned_cpus']
                    total_memory_usage = cell['memory_usage'] + node[
                        'memory_usage']
                    cell_info = dict(cpuset=cell['cpuset'],
                                     memory=cell['memory'],
                                     cpu_usage=total_cpu_usage,
                                     pinned_cpus=list(set(total_pinned_cpus)),
                                     memory_usage=total_memory_usage,
                                     id=cell['id'])
                    total_numa_topologies.append(cell_info)
    if nova_numa_topology is not None and zun_numa_topology is None:
        for cell in nova_numa_topology['nova_numa_topology']:
            total_cpu_usage = cell['cpu_usage']
            total_pinned_cpus = cell['pinned_cpus']
            total_memory_usage = cell['memory_usage']
            cell_info = dict(cpuset=cell['cpuset'], memory=cell['memory'],
                             cpu_usage=total_cpu_usage,
                             pinned_cpus=total_pinned_cpus,
                             memory_usage=total_memory_usage, id=cell['id'])
            total_numa_topologies.append(cell_info)
    if nova_numa_topology is None and zun_numa_topology is not None:
        for node in zun_numa_topology['zun_numa_topology']:
            total_cpu_usage = node['cpu_usage']
            total_pinned_cpus = node['pinned_cpus']
            total_memory_usage = node['memory_usage']
            cell_info = dict(cpuset=node['cpuset'], memory=node['memory'],
                             cpu_usage=total_cpu_usage,
                             pinned_cpus=total_pinned_cpus,
                             memory_usage=total_memory_usage, id=node['id'])
            total_numa_topologies.append(cell_info)
    numa_topologies = {'uuid': uuid,
                       'numa_topologies': total_numa_topologies,
                       }
    response.body = encodeutils.to_utf8(json.dumps(numa_topologies))
    req.response.content_type = 'application/json'
    return req.response


@wsgi_wrapper.PlacementWsgify
@util.require_content('application/json')
def update_numa_topologies_for_resource_provider(req):
    context = req.environ['placement.context']
    context.can(policies.UPDATE)
    # want_version = req.environ[microversion.MICROVERSION_ENVIRON]
    uuid = util.wsgi_path_item(req.environ, 'uuid')
    try:
        data = util.extract_json(req.body, schema.PUT_NUMA_TOPOLOGIES_SCHEMA)
    except jsonschema.ValidationError:
        raise webob.exc.HTTPBadRequest(
            _('The NUMA topology is invalid.'))
    numa_topology = rp_obj.NUMATopology(context)
    numa_topology.uuid = data['uuid']
    try:
        numa_topology.get_by_resource_provider_uuid(context, uuid)
    except exception.NUMATopologyNotFound:
        if 'nova_numa_topology' in data:
            numa_topology.nova_numa_topology = json.dumps(
                {"nova_numa_topology": data["nova_numa_topology"]})
        if 'zun_numa_topology' in data:
            numa_topology.zun_numa_topology = json.dumps(
                {"zun_numa_topology": data["zun_numa_topology"]})
        numa_topology.create()
    if 'nova_numa_topology' in data:
        numa_topology.nova_numa_topology = json.dumps(
            {"nova_numa_topology": data["nova_numa_topology"]})
        numa_topology.update_nova()
    elif 'zun_numa_topology' in data:
        numa_topology.zun_numa_topology = json.dumps(
            {"zun_numa_topology": data["zun_numa_topology"]})
        numa_topology.update_zun()
    # print('NUMATopology_obj', '+' * 30, numa_topology)
    req.response.body = encodeutils.to_utf8(str(data))
    req.response.content_type = 'application/json'
    return req.response


@wsgi_wrapper.PlacementWsgify
@util.require_content('application/json')
def delete_numa_topologies_for_resource_provider(req):
    context = req.environ['placement.context']
    context.can(policies.DELETE)
    uuid = util.wsgi_path_item(req.environ, 'uuid')
    numa_topology = rp_obj.NUMATopology.get_by_resource_provider_uuid(context,
                                                                      uuid)
    try:
        numa_topology.delete_by_resource_provider_uuid(context,
                                                       numa_topology.uuid)
    except exception.ConcurrentUpdateDetected as e:
        raise webob.exc.HTTPConflict(e.format_message(),
                                     comment=errors.CONCURRENT_UPDATE)
    req.response.status = 204
    req.response.content_type = None
    return req.response
