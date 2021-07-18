#!/usr/bin/python
from owlready2 import *
import time

start_time = time.time()

my_world = World(filename="./reasoning.sqlite")
my_world = World()
onto = my_world.get_ontology("../rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality.owl").load()
# data = my_world.get_ontology("../rdf/example/PLOD_r3.rdf").load()
data = my_world.get_ontology("./test.rdf").load()
sync_reasoner([onto,data])
my_world.save()

results = list(my_world.sparql("""
    PREFIX plod: <http://plod.info/rdf/>
    SELECT DISTINCT * WHERE {
        ?s rdf:type plod:HighLevelCloseContact .
    } limit 1000"""))
ids = []
for result in results:
  ids.append(result[0].iri)  
ids.sort()
# print(ids)
print("plod:HighLevelCloseContact count by reasoning.py: %s" % (len(ids)-1))

results = list(my_world.sparql("""
    PREFIX plod: <http://plod.info/rdf/>
    SELECT DISTINCT * WHERE {
        ?s rdf:type plod:MediumLevelCloseContact .
    } limit 1000"""))
ids = []
for result in results:
  ids.append(result[0].iri)  
ids.sort()
# print(ids)
print("plod:MediumLevelCloseContact count by reasoning.py: %s" % len(ids))

print("--- %s seconds ---" % (time.time() - start_time))