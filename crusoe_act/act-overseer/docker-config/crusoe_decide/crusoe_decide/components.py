""" Module which contains function determining possible configurations of a mission."""


def get_mission_components(data, root):
    """
    Returns all possible combinations of components for a mission which is specified by its
    root node (according to the constrained AND-OR tree). This is done by traversing the tree
    until we reach the LEAFs - hosts of configuration.

    :param data: json containing constrained AND-OR tree
    :param root: id of root node for the mission
    :return: configurations of the mission
    """

    partial_result = [[root]]
    complete_result = []
    while partial_result:
        vertex_list = partial_result.pop(0)
        i = 0
        original_length = len(vertex_list)
        while i < len(vertex_list):
            entity_id = vertex_list[i]
            if services_contain_id(data['nodes']['services'], entity_id):
                vertex_list.pop(i)
                for edge in data['relationships']['one_way']:
                    if edge['from'] == entity_id:
                        vertex_list.append(edge['to'])
                partial_result.append(vertex_list)
                break
            elif hosts_contain_id(data['nodes']['hosts'], entity_id):
                i += 1
                continue
            elif entity_id in data['nodes']['aggregations']['and']:
                vertex_list.pop(i)
                for edge in data['relationships']['one_way']:
                    if edge['from'] == entity_id:
                        vertex_list.append(edge['to'])
                partial_result.append(vertex_list)
                break
            elif entity_id in data['nodes']['aggregations']['or']:
                vertex_list.pop(i)
                edge_ends = []
                for edge in data['relationships']['one_way']:
                    if edge['from'] == entity_id:
                        edge_ends.append(edge['to'])
                for end in edge_ends:
                    partial_result.append(vertex_list + [end])
                break
            elif missions_contain_id(data['nodes']['missions'], entity_id):
                vertex_list.pop(i)
                for edge in data['relationships']['one_way']:
                    if edge['from'] == entity_id:
                        vertex_list.append(edge['to'])
                partial_result.append(vertex_list)
                break
        if i == original_length:
            # contains only hosts
            complete_result.append(set(vertex_list))
    return complete_result


def hosts_contain_id(hosts_data, host_id):
    """
    True if host_id is id of a host.

    :param hosts_data: list of hosts
    :param host_id: id of a host
    :return: True or False
    """
    for host in hosts_data:
        if host_id == host['id']:
            return True
    return False


def services_contain_id(services_data, service_id):
    """
    Tests if service_id is id of service.

    :param services_data: list of services
    :param service_id: id of service
    :return: True if service_id is service
    """
    for service in services_data:
        if service_id == service['id']:
            return True
    return False


def components_contain_id(components_data, component_id):
    """
    Tests whether component_id is id of component.

    :param components_data: list of components
    :param component_id: id of component
    :return: True if component_id is component
    """
    for component in components_data:
        if component_id == component['id']:
            return True
    return False


def missions_contain_id(missions_data, mission_id):
    """
    Tests whether mission_id is id of mission.

    :param missions_data: list of missions
    :param mission_id: id of mission
    :return: True if mission_id is mission
    """
    for mission in missions_data:
        if mission_id == mission['id']:
            return True
    return False
