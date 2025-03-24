from rdflib import Graph, Namespace
from rdflib.collection import Collection

geo = Namespace("http://www.opengis.net/ont/geosparql#")

def get_namespace(graph):
    """Extract the primary namespace dynamically from the TTL file."""
    for prefix, uri in graph.namespaces():
        if "example.org" in str(uri):
            return Namespace(str(uri))
    raise ValueError("No appropriate namespace found in the file.")

# def get_top_level_resource(graph, ns):
#     """
#     Identify the top-level resource dynamically.
#     Assumes the top-level resource has children (ns:hasChildDigitalTwin).
#     """
#     for subject in graph.subjects():
#         if (subject, ns.hasChildDigitalTwin, None) in graph:
#             return subject
#     raise ValueError("No top-level resource with 'hasChildDigitalTwin' found.")

def get_top_level_resource(graph, ns):
    """
    Identify the top-level resource dynamically.
    The top-level resource has children (ns:hasChildDigitalTwin) 
    but is not itself a child of any other resource.
    """
    candidates = set(subject for subject in graph.subjects(predicate=ns.hasChildDigitalTwin))

    children = set(child for child in graph.objects(predicate=ns.hasChildDigitalTwin))

    # Top-level resources are candidates that aren't children themselves
    top_level_resources = candidates - children

    if top_level_resources:
        # Usually, there's only one top-level resource; pick one.
        return top_level_resources.pop()
    
    raise ValueError("No top-level resource found.")

def gather_info(graph, resource, ns, visited=None, parent=None):
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
    
    geoLocation = []
    for geoLoc in graph.objects(resource, ns.hasGeoLocation):
        latitude = next(graph.objects(geoLoc, ns.latitude), 0)
        longitude = next(graph.objects(geoLoc, ns.longitude), 0)
        altitude = next(graph.objects(geoLoc, ns.altitude), 0)

        # latitude = latitude.toPython() if latitude else None
        # longitude = longitude.toPython() if longitude else None
        # altitude = altitude.toPython() if altitude else None

        geoLocation.append({'latitude': latitude, 'longitude': longitude, 'altitude': altitude})
    
    meshGeometry = []
    for mesh in graph.objects(resource, ns.hasMeshGeometry):
        vertices_list = graph.value(mesh, ns.hasVertices)
        if vertices_list:
            collection = Collection(graph, vertices_list)
            vertices = []
            for vertex in collection:
                wkt_point = graph.value(vertex, geo.asWKT)
                if wkt_point:
                    vertices.append(str(wkt_point))
            meshGeometry.append({
                'mesh': mesh.split('#')[-1],
                'vertices': vertices
            })

    # Determine parent's local name (if any)
    if parent is not None:
        parent_local_name = parent.split('#')[-1]
    else:
        parent_local_name = None

    results = [{
        'resource': resource,
        'parent': parent_local_name,
        'sensors': sensors,
        'actuators': actuators,
        'geoLocation': geoLocation,
        'meshGeometry': meshGeometry
    }]

    # Recurse into child digital twins
    children = set(graph.objects(resource, ns.hasChildDigitalTwin))
    for child in children:
        results.extend(gather_info(graph, child, ns, visited, parent=resource))
    return results

def main():
    # Load the TTL file into an RDF graph
    g = Graph()
    g.parse("dt.ttl", format="turtle")

    # Dynamically determine namespace
    NS0 = get_namespace(g)

    # Dynamically identify top-level resource
    atlas_uri = get_top_level_resource(g, NS0)

    # Gather info starting from the top-level resource
    all_info = gather_info(g, atlas_uri, NS0)

    # Print out the gathered info, including parent info if available
    for item in all_info:
        resource_local_name = item['resource'].split('#')[-1]
        if item['parent']:
            print(f"\nResource: {resource_local_name} (Parent: {item['parent']})")
        else:
            print(f"\nResource: {resource_local_name} (Parent: None)")

        # Print sensors
        if item['sensors']:
            print("  Sensors:")
            for sensor in item['sensors']:
                print(f"    - ID: {sensor['id']} (Type: {sensor['type']})")
        else:
            print("  Sensors: None")

        # Print actuators
        if item['actuators']:
            print("  Actuators:")
            for actuator in item['actuators']:
                print(f"    - ID: {actuator['id']} (Type: {actuator['type']})")
        else:
            print("  Actuators: None")
        
        if item['geoLocation']:
            print("  Geolocation:")
            for geoLoc in item['geoLocation']:
                print(f"    - latitude: {geoLoc['latitude']}")
                print(f"    - longitude: {geoLoc['longitude']}")
                print(f"    - altitude: {geoLoc['altitude']}")
        else:
            print("  geoLocation: None")
        
        if item['meshGeometry']:
            print("  Mesh Geometry:")
            for mesh in item['meshGeometry']:
                print(f"    Mesh: {mesh['mesh']}")
                for vertex in mesh['vertices']:
                    print(f"      - Vertex: {vertex}")
        else:
            print("  Mesh Geometry: None")

if __name__ == "__main__":
    main()