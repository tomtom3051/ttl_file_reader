from rdflib import Graph, Namespace

def get_namespace(graph):
    """Extract the primary namespace dynamically from the TTL file."""
    # Extract the first defined namespace
    for prefix, uri in graph.namespaces():
        if "example.org" in str(uri):
            return Namespace(str(uri))  # Return as RDFLib's Namespace object
    raise ValueError("No appropriate namespace found in the file.")

def get_top_level_resource(graph, ns):
    """
    Identify the top-level resource dynamically.
    Assumes the top-level resource has children (ns:hasChildDigitalTwin).
    """
    for subject in graph.subjects():
        if (subject, ns.hasChildDigitalTwin, None) in graph:
            return subject
    raise ValueError("No top-level resource with 'hasChildDigitalTwin' found.")

def gather_info(graph, resource, ns, visited=None):
    if visited is None:
        visited = set()

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

    results = [{
        'resource': resource,
        'sensors': sensors,
        'actuators': actuators
    }]

    for child in children:
        results.extend(gather_info(graph, child, ns, visited))

    return results


def main():
    # Load the TTL file into an RDF graph
    g = Graph()
    g.parse("digital_twin.ttl", format="turtle")

    # Dynamically determine namespace
    NS0 = get_namespace(g)

    # Dynamically identify top-level resource
    atlas_uri = get_top_level_resource(g, NS0)

    # Gather info for Atlas_floor_3 and all its children
    all_info = gather_info(g, atlas_uri, NS0)

    # Print them out
    for item in all_info:
        resource_local_name = item['resource'].split('#')[-1]
        print(f"\nResource: {resource_local_name}")

        # SENSORS
        if item['sensors']:
            print("  Sensors:")
            for sensor in item['sensors']:
                print(f"    - ID: {sensor['id']} (Type: {sensor['type']})")
        else:
            print("  Sensors: None")

        # ACTUATORS
        if item['actuators']:
            print("  Actuators:")
            for actuator in item['actuators']:
                print(f"    - ID: {actuator['id']} (Type: {actuator['type']})")
        else:
            print("  Actuators: None")


if __name__ == "__main__":
    main()