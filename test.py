from rdflib import Graph, Namespace, URIRef

def gather_info(graph, resource, ns, visited=None):
    """
    Recursively gather sensor and actuator info for `resource`
    and all its children.
    
    :param graph: The RDF graph to query
    :param resource: A URIRef representing the resource
    :param ns: The main namespace (e.g., http://www.example.org/digitaltwin#)
    :param visited: A set of resources already visited (to avoid loops)
    :return: A list of dicts, where each dict has:
             {
               'resource': URIRef(...),
               'sensors': [URIRef(...)],
               'actuators': [URIRef(...)]
             }
    """
    if visited is None:
        visited = set()

    # If we've already visited this resource, avoid infinite loops
    if resource in visited:
        return []
    visited.add(resource)

    # Collect sensor details
    sensors = []
    for sensor in graph.objects(resource, ns.hasSensor):
        sensor_id = next(graph.objects(sensor, ns.sensorID), "Unknown ID")
        sensor_type = next(graph.objects(sensor, ns.sensorType), "Unknown Type")
        sensors.append({'id': sensor_id, 'type': sensor_type})

    # Collect actuator details
    actuators = []
    for actuator in graph.objects(resource, ns.hasActuator):
        actuator_id = next(graph.objects(actuator, ns.actuatorID), "Unknown ID")
        actuator_type = next(graph.objects(actuator, ns.actuatorType), "Unknown Type")
        actuators.append({'id': actuator_id, 'type': actuator_type})

    # Look for child digital twins
    children = set(graph.objects(resource, ns.hasChildDigitalTwin))

    # Store info for this resource
    results = [{
        'resource': resource,
        'sensors': sensors,
        'actuators': actuators
    }]

    # Recursively gather info for each child
    for child in children:
        results.extend(gather_info(graph, child, ns, visited))

    return results

def main():
    # Load the TTL file into an RDF graph
    g = Graph()
    g.parse("digital_twin.ttl", format="turtle")

    # Define the main namespace used in the file
    NS0 = Namespace("http://www.example.org/digitaltwin#")

    # URI of our top-level resource
    atlas_uri = URIRef("http://www.example.org/digitaltwin#Atlas_floor_3")

    # Gather info for Atlas_floor_3 and all its children
    all_info = gather_info(g, atlas_uri, NS0)

    # Print them out
    for item in all_info:
        # item['resource'] is a URIRef like: http://www.example.org/digitaltwin#Room_10
        resource_local_name = item['resource'].split('#')[-1]
        print(f"\nResource: {resource_local_name}")

        # SENSORS
        if item['sensors']:
            print("  Sensors:")
            for s in item['sensors']:
                print(f"    - ID: {s['id']} (Type: {s['type']})")
        else:
            print("  Sensors: None")

        # ACTUATORS
        if item['actuators']:
            print("  Actuators:")
            for a in item['actuators']:
                print(f"    - ID: {a['id']} (Type: {a['type']})")
        else:
            print("  Actuators: None")

# def main():
#     ###
#     ###
#     ### CODE TO PRINT A ROOM ALONG WITH ITS DTS
#     ###
#     ###

#     # Load the TTL file into a graph
#     g = Graph()
#     g.parse("digital_twin.ttl", format="turtle")

#     # Define the main namespace used in the file
#     NS0 = Namespace("http://www.example.org/digitaltwin#")

#     # The full URI for Atlas_floor_3
#     atlas_uri = URIRef("http://www.example.org/digitaltwin#Atlas_floor_3")

#     # Collect sensors and actuators
#     sensors = set(g.objects(atlas_uri, NS0.hasSensor))
#     actuators = set(g.objects(atlas_uri, NS0.hasActuator))

#     # Print name of the resource
#     # (Local name is everything after the '#', e.g. "Atlas_floor_3")
#     atlas_name = atlas_uri.split('#')[-1]
#     print(f"Resource name: {atlas_name}")

#     # Print sensors
#     print("Sensors:")
#     for sensor in sensors:
#         # sensor is a URI, so get its local part as well
#         sensor_local_name = sensor.split('#')[-1]
#         print(f"  - {sensor_local_name}")

#     # Print actuators
#     print("Actuators:")
#     for actuator in actuators:
#         actuator_local_name = actuator.split('#')[-1]
#         print(f"  - {actuator_local_name}")

    ###
    ###
    ### CODE TO PRINT EVERY LINE IN THE TTL
    ###
    ###
    # # Replace 'digital_twin.ttl' with the exact file name if it's different
    # ttl_file = 'digital_twin.ttl'
    
    # # Open the file in read mode
    # with open(ttl_file, 'r', encoding='utf-8') as file:
    #     # Read and print each line
    #     for line in file:
    #         # Strip trailing newline characters before printing (optional)
    #         print(line.rstrip())

if __name__ == "__main__":
    main()