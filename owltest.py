#!/usr/bin/python
from owlready2 import *
my_world = World()
my_world.set_backend(filename="./test.sqlite")
onto = my_world.get_ontology(
    "rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality.owl").load()
# my_world.save()
# classes = list(onto.classes())
# print(classes)

# data = my_world.get_ontology("rdf/example/PLOD_r2.2.rdf").load()
# sync_reasoner([onto,data])

# places
places = list(my_world.sparql("""
    PREFIX plod: <http://plod.info/rdf/>
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT * WHERE {
        ?s a owl:Class ;
           rdfs:subClassOf+ schema:Place .
    } limit 1000"""))

place_samples = []
for place in places:
    # print(place[0])
    affords = list(my_world.sparql("""
        PREFIX plod: <http://plod.info/rdf/>
        PREFIX schema: <http://schema.org/>
        SELECT DISTINCT * WHERE {
            <%s> rdfs:subClassOf [ owl:onProperty plod:afford ; owl:hasValue ?o2 ] .
            ?o2 a ?o3
        } limit 100""" % (place[0].iri)))
    p = dict(name=place[0].name, iri=place[0].iri, DropletReachableActivity=0)
    # print(affords)
    for afford in affords:
        if(hasattr(afford[1], 'iri') and afford[1].iri == 'http://plod.info/rdf/DropletReachableActivity'):
            p['DropletReachableActivity'] += 1
    place_samples.append(p)
print(place_samples)


# results = list(my_world.sparql("""
#     PREFIX plod: <http://plod.info/rdf/>
#     PREFIX schema: <http://schema.org/>
#     SELECT DISTINCT * WHERE {
#         plod:Bar rdfs:subClassOf [ owl:onProperty plod:afford ; owl:hasValue ?o2 ] .
#         ?o2 a ?o3
#     } limit 100"""))

# for result in results:
#     print(result)

# results = list(my_world.sparql("""
#     PREFIX plod: <http://plod.info/rdf/>
#     PREFIX schema: <http://schema.org/>
#     SELECT DISTINCT * WHERE {
#         ?s rdfs:subClassOf ?o .
#         FILTER (?o IN ( plod:Airplane, plod:Bus, plod:Railway, plod:Subway, plod:Taxi, plod:Bar, plod:CoffeeShop, plod:ConcertHall, plod:DentalClinic, plod:GroceryStore, plod:Gym, plod:HairSalon, plod:Home, plod:Hospital, plod:IndoorPartyVenue, plod:IndoorSportsFacility, plod:LiveTheater, plod:MedicalOffice, plod:MovieTheater, plod:Museum, plod:Nightclub, plod:Office, plod:ReligiousFacility, plod:Restaurant, plod:RetailStore, plod:School, plod:OutdoorRestaurant, plod:OutdoorSportsFacility ) )
#     } limit 100"""))

# for result in results:
#     print(result[0])

# results = list(my_world.sparql("""
#     PREFIX plod: <http://plod.info/rdf/>
#     PREFIX schema: <http://schema.org/>
#     SELECT DISTINCT ?s3 ?o2 WHERE {
#         ?s rdfs:subClassOf ?o .
#         FILTER (?o IN ( plod:Public_transportation, plod:IndoorFacility, plod:OutdoorFacility ) ) .
#         ?o rdfs:subClassOf ?s3
#         ?s3 a ?o2
#     } limit 100"""))

# for result in results:
#     print(result)


# results = list(my_world.sparql("""
#     PREFIX plod: <http://plod.info/rdf/>
#     PREFIX schema: <http://schema.org/>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     SELECT DISTINCT * WHERE {
#         ?s rdfs:subClassOf schema:Place .
#     } limit 100"""))
# print(results)
