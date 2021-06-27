#!/usr/bin/python
from owlready2 import *
my_world = World()
my_world.set_backend(filename="./test.sqlite")
onto = my_world.get_ontology(
    "rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality.owl").load()
my_world.save()
# classes = list(onto.classes())
# print(classes)

# data = my_world.get_ontology("rdf/example/PLOD_r2.2.rdf").load()
# sync_reasoner([onto,data])
prefix = """
    PREFIX plod: <http://plod.info/rdf/>
    PREFIX schema: <http://schema.org/>
"""

places = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a owl:Class ;
           rdfs:subClassOf+ schema:Place .
    } limit 1000""" % (prefix)))

place_samples = []
for place in places:
    # print(place[0])
    affords = list(my_world.sparql("""
        %s
        SELECT DISTINCT * WHERE {
            <%s> rdfs:subClassOf [ owl:onProperty plod:afford ; owl:hasValue ?o2 ] .
            ?o2 a ?o3
        } limit 1000""" % (prefix, place[0].iri)))
    p = dict(name=place[0].name, iri=place[0].iri, DropletReachableActivity=0)
    for afford in affords:
        if(hasattr(afford[1], 'iri') and afford[1].iri == 'http://plod.info/rdf/DropletReachableActivity'):
            p['DropletReachableActivity'] += 1
    place_samples.append(p)
print(place_samples)

activity_types = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a owl:Class ;
           rdfs:subClassOf+ plod:Activity .
    } limit 1000""" % (prefix)))

activity_samples = []
for activity_type in activity_types:
    activities = list(my_world.sparql("""
        %s
        SELECT DISTINCT * WHERE {
            ?s a <%s>
        } limit 1000""" % (prefix, activity_type[0].iri)))
    for activity in activities:
        activity_samples.append(dict(name=activity[0].name, iri=activity[0].iri, isDropletReachableActivity=activity_type[0].iri == 'http://plod.info/rdf/DropletReachableActivity'))
print(activity_samples)

risk_activity_situations = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a plod:RiskActivitySituation .
    } limit 1000""" % (prefix)))

risk_activity_situations_samples = []
for risk_activity_situation in risk_activity_situations:
    s = dict(name=risk_activity_situation[0].name, iri=risk_activity_situation[0].iri)
    risk_activity_situations_samples.append(dict(name=risk_activity_situation[0].name, iri=risk_activity_situation[0].iri))
print(risk_activity_situations_samples)
