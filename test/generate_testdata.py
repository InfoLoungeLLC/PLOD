#!/usr/bin/python
'''
# plod:HighLevelCloseContact を任意の割合で含むschema:Eventインスタンスを指定の個数生成する
plod:HighLevelCloseContact を満たすclassの条件
下記の(1. or 2.) and 3. and 4.であること
1. schema:locationが存在し、それの指すリソースの型がplod:DropletReachableActivityをplod:affordするプロパティが2つ以上持っている。
2. plod:DropletReachableActivity型のschema:actionが2つ以上存在する
3. plod:timeが存在し、15分以上である
4. plod:RiskActivitySituation型のplod:situationOfActivityが1つ以上存在する
(疑問点) schema:Eventに含まれるplod:agentの数はplod:HighLevelCloseContactの評価に使用していない？

## 処理手順

### 事前準備
SARS-CoV-2_Infection_Risk_Ontology_cardinality.owlをパースして
1. schema:Placeを継承するクラスを再帰的に抽出してschema:locationの候補を取得
    - それぞれがplod:DropletReachableActivityを2つ以上持つかを判定しておく
2. plod:Activityを継承するクラスを再帰的に抽出してschema:actionの候補を取得
    - それぞれがplod:DropletReachableActivity型かを判定しておく
3. plod:RiskActivitySituation型のクラスを抽出してplod:situationOfActivityの候補を取得

### テストデータ生成
- 1.の候補を元にschema:locationの候補となるインスタンスを生成
- schema:Eventを作成し、rdf:about="http://plod.info/rdf/id/event_{xxx}"で一意となるURIを生成
- schema:locationプロパティを1.の候補から任意に選択し、plod:DropletReachableActivityを2つ以上持つかの判定を内部保持
- plod:timeのダミーインスタンスを
```
  <time:Interval rdf:about="http://plod.info/rdf/id/time_{xxx}">
    <time:hasDuration>
      <time:TemporalDuration rdf:about="http://plod.info/rdf/id/duration_a42">
        <time:numericDuration rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">{decimal}</time:numericDuration>
      </time:TemporalDuration>
    </time:hasDuration>
  </time:Interval>
```
の形式で生成し、schema:Eventのplod:timeプロパティで参照。15秒以上(900秒以上）かどうかの判定を内部保持

- plod:agentを`<plod:agent rdf:resource="http://plod.info/rdf/id/person_{xxx}"/>`の形式で適当な数生成
- plod:actionを任意の数生成。含まれるplod:DropletReachableActivity型の種類が2以上かどうかを判定して内部保持
- plod:situationOfActivityを任意の数生成。含まれるplod:RiskActivitySituation型の種類が2以上かどうかを判定して内部保持
- 生成が完了したら、そのschema:Eventがplod:HighLevelCloseContactかどうかを判定。例えば100個テストデータを生成した後、そのうちいくつがplod:HighLevelCloseContactになるはずかをコメント等で出力する

---

# plod:HighLevelCloseContact を満たすclassの条件
下記の(1. or 2.) and 3. and 4.であること
1. schema:locationが存在し、それの指すリソースの型がplod:DropletReachableActivityをplod:affordするプロパティが2つ以上持っている
2. plod:DropletReachableActivity型のschema:actionが2つ以上存在する
3. plod:timeが存在し、15以上である
4. plod:RiskActivitySituation型のplod:situationOfActivityが1つ以上存在する

# plod:MediumLevelCloseContact を満たすclassの条件
下記の(1. or 2.) and 3. and 4.であること
1. schema:locationが存在し、それの指すリソースの型がplod:DropletReachableActivityをplod:affordするプロパティを1つ持っている
2. plod:DropletReachableActivity型のschema:actionが1つ存在する
3. plod:timeが存在し、15以上である
4. plod:RiskActivitySituation型のplod:situationOfActivityが1つ以上存在する

# plod:HighLevelCrowding を満たすclassの条件
下記の 1. and 2.であること
1. plod:RiskActivitySituation型のplod:situationOfActivityが1つ以上存在する
2. plod:RiskSpaceSituation型のplod:situationOfSpaceが2つ以上存在する

# plod:MediumLevelCrowding を満たすclassの条件
下記の 1. and 2.であること
1. plod:RiskActivitySituation型のplod:situationOfActivityが1つ以上存在する
2. plod:RiskSpaceSituation型のplod:situationOfSpaceが1つ存在する

# plod:HighLevelClosedSpace を満たすclassの条件
下記の(1. or 2.) and 3. であること
1. plot:isSituationOfが存在し、plot:IndoorFacilityである
2. plot:isSituationOfが存在し、plot:Public_transportationである
3. plod:RiskSpaceSituation型のplod:situationOfSpaceが1つ以上存在する

# plod:MediumLevelClosedSpace を満たすclassの条件
下記の(1. or 2.) であること
1. plot:isSituationOfが存在し、plot:IndoorFacilityである
2. plot:isSituationOfが存在し、plot:Public_transportationである
'''
from owlready2 import *
from rdflib import Graph, Literal, BNode, RDF, RDFS, Namespace, URIRef
from rdflib.namespace import XSD
import time
import random
import sys
import csv
import select_methods as sl

args = sys.argv
data_count = int(args[1])

'''
不可能な組み合わせ(csv順)
h-h-l
h-m-h
h-m-h
m-h-l
m-m-h
m-m-m
l-m-h
l-m-m
'''

# read CSV
with open('sample.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    case_sample = [row for row in reader]

case = case_sample[int(args[2])]

first_count = int(data_count * int(case[4]) / 100)
second_count = int(data_count * int(case[8]) / 100)
third_count = data_count - first_count - second_count

my_world = World()
my_world.set_backend(filename="./test.sqlite")
onto = my_world.get_ontology(
    "../rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality_ExactlyToMin.owl").load()
my_world.save()

prefix = """
    PREFIX plod: <http://plod.info/rdf/>
    PREFIX schema: <http://schema.org/>
"""

samples = {}

places = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a owl:Class ;
           rdfs:subClassOf+ schema:Place .
    } limit 1000""" % (prefix)))

samples['place'] = []
for place in places:
    affords = list(my_world.sparql("""
        %s
        SELECT DISTINCT * WHERE {
            <%s> rdfs:subClassOf [ owl:onProperty plod:afford ; owl:hasValue ?o2 ] .
            ?o2 a ?o3
        } limit 1000""" % (prefix, place[0].iri)))
    p = {'name': place[0].name, 'iri': place[0].iri,
         'droplet_reachable_activity': 0}
    for afford in affords:
        if(hasattr(afford[1], 'iri') and afford[1].iri == 'http://plod.info/rdf/DropletReachableActivity'):
            p['droplet_reachable_activity'] += 1
    samples['place'].append(p)

activity_types = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a owl:Class ;
           rdfs:subClassOf+ plod:Activity .
    } limit 1000""" % (prefix)))

samples['activity'] = []
samples['reachable_activity'] = []
samples['not_reachable_activity'] = []

for activity_type in activity_types:
    activities = list(my_world.sparql("""
        %s
        SELECT DISTINCT * WHERE {
            ?s a <%s>
        } limit 1000""" % (prefix, activity_type[0].iri)))
    for activity in activities:
        sample = {'name': activity[0].name, 'iri': activity[0].iri,
                  'is_droplet_reachable_activity': activity_type[0].iri == 'http://plod.info/rdf/DropletReachableActivity'}
        samples['activity'].append(sample)
        if sample["is_droplet_reachable_activity"]:
            samples['reachable_activity'].append(sample)
        else:
            samples['not_reachable_activity'].append(sample)


risk_activity_situations = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a plod:RiskActivitySituation .
    } limit 1000""" % (prefix)))

samples['risk_activity_situation'] = []
for risk_activity_situation in risk_activity_situations:
    samples['risk_activity_situation'].append(
        {'name': risk_activity_situation[0].name, 'iri': risk_activity_situation[0].iri})


risk_space_situations = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a plod:RiskSpaceSituation .
    } limit 1000""" % (prefix)))

samples['risk_space_situation'] = []
for risk_space_situation in risk_space_situations:
    samples['risk_space_situation'].append(
        {'name': risk_space_situation[0].name, 'iri': risk_space_situation[0].iri})

situation_types = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        {
            ?s a owl:Class ;
            rdfs:subClassOf+ plod:IndoorFacility .
        }
        UNION
        {
            ?s a owl:Class ;
            rdfs:subClassOf+ plod:Public_transportation .
        }
    } limit 1000""" % (prefix)))

samples['situation_type'] = []
for situation_type in situation_types:
    samples['situation_type'].append({
        'name': situation_type[0].name, 'iri': situation_type[0].iri})

    # situations = list(my_world.sparql("""
    #     %s
    #     SELECT DISTINCT * WHERE {
    #         ?s a <%s>
    #     } limit 1000""" % (prefix, situation_type[0].iri)))
    # for situation in situations:
    #     situation_samples.append({'name': situation[0].name, 'iri': situation[0].iri,
    #                                  'isSituationOf': situation_type[0].iri == 'http://plod.info/rdf/isSituationOf'})

store = Graph()
schema = Namespace("https://schema.org/")
time = Namespace("http://www.w3.org/2006/time#")

store.bind("schema", schema)
store.bind("time", time)

g = Graph()
g.parse("../rdf/PLOD_schema.owl", format="xml")
plod = Namespace("http://plod.info/rdf/")
store.bind("plod", plod)

for place_sample in samples['place']:
    place_sample_uri = URIRef(
        "http://plod.info/rdf/%s" % place_sample['name'])
    store.add((place_sample_uri, RDFS.label, Literal(place_sample['name'])))
    store.add((place_sample_uri, RDF.type, URIRef(place_sample['iri'])))

# samples['person'] = []
# for i in range(data_count):
#     person_sample_uri = URIRef(
#         "http://plod.info/rdf/id/person_%s" % i)
#     store.add((person_sample_uri, RDF.type, schema.Person))
#     store.add((person_sample_uri, RDFS.label, Literal("person_%s" % i)))
#     samples['person'].append(person_sample_uri)

# high_events = []

high_level_close_contact_count = 0
medium_level_close_contact_count = 0
high_level_crowding_count = 0
medium_level_crowding_count = 0
high_level_closed_space_count = 0
medium_level_closed_space_count = 0

for i in range(data_count):
    if i < first_count:
        levels = {
            'close_contact': case[1],
            'crowding': case[3],
            'closed_space': case[2]
        }
    elif i < first_count + second_count:
        levels = {
            'close_contact': case[5],
            'crowding': case[7],
            'closed_space': case[6]
        }
    else:
        levels = {
            'close_contact': case[9],
            'crowding': case[11],
            'closed_space': case[10]
        }

    uri = "http://plod.info/rdf/id/event_%s" % i
    event_uri = URIRef(uri)
    store.add((event_uri, RDF.type, schema.Event))
    store.add((event_uri, RDFS.label, Literal("event_%s" % i)))

    location, actions = sl.location_and_action(
        levels, samples['place'], samples['reachable_activity'], samples['not_reachable_activity'])

    location_uri = URIRef("http://plod.info/rdf/%s_%s" % (location['name'], i))
    location_uri_noindex = URIRef("http://plod.info/rdf/%s" % location['name'])
    store.add((event_uri, schema.location, location_uri))
    store.add((location_uri, RDF.type, location_uri))
    store.add((location_uri, RDF.type, location_uri_noindex))


    droplet_reachable_activity_count = 0
    for action in actions:
        store.add((event_uri, plod.action, URIRef(
            "http://plod.info/rdf/%s" % action['name'])))
        if(action["is_droplet_reachable_activity"]):
            droplet_reachable_activity_count += 1

    # person_count = random.randint(1, 4)
    # persons = random.sample(samples['person'], person_count)
    # for person in persons:
    #     store.add((event_uri, plod.agent, person))

    risk_activity_situation_count, risk_activity_situations = sl.activity_situation(
        levels, samples['risk_activity_situation'])

    for risk_activity_situation in risk_activity_situations:
        store.add((event_uri, plod.situationOfActivity, URIRef(
            "http://plod.info/rdf/%s" % risk_activity_situation['name'])))

    time_uri = URIRef("http://plod.info/rdf/id/time_%s" % i)
    store.add((time_uri, RDF.type, time.Interval))
    store.add((event_uri, plod.time, time_uri))

    duration = sl.random_duration(levels)

    time_temporal_duration_uri = URIRef(
        "http://plod.info/rdf/id/duration_%s" % i)
    store.add((time_temporal_duration_uri, RDF.type, time.TemporalDuration))
    store.add((time_uri, time.hasDuration, time_temporal_duration_uri))
    store.add((time_temporal_duration_uri, time.numericDuration,
               Literal(duration, datatype=XSD.decimal)))


    situation_uri = URIRef("http://plod.info/rdf/id/situation_%s" % i)
    store.add((situation_uri, RDF.type, plod.Situation))
    store.add((situation_uri, plod.isSituationOf, location_uri))


    risk_spaces = sl.space_situation(levels, samples['risk_space_situation'])
    risk_spaces_count = 0
    if risk_spaces != None:
        for risk_space in risk_spaces:
            risk_spaces_count += 1
            store.add((situation_uri, plod.situationOfSpace, URIRef(
                "http://plod.info/rdf/%s" % risk_space['name'])))


    # high_events.append({'uri': uri, 'iri': place[0].iri, 'location_has_one_more_than_droplet_reachable_activity': location['droplet_reachable_activity'] > 1,
    #                     'event_has_one_more_than_droplet_reachable_activity': droplet_reachable_activity_count > 1, 'event_has_one_risk_activity_situation': risk_activity_situation_count > 0, 'longer_than_15': duration > 15})

  
    if (location['droplet_reachable_activity'] > 1 or droplet_reachable_activity_count > 1) and risk_activity_situation_count > 0 and duration > 15:
        high_level_close_contact_count += 1
    
    if ((location['droplet_reachable_activity'] == 1 and droplet_reachable_activity_count <= 1) or (droplet_reachable_activity_count == 1 and location['droplet_reachable_activity'] <= 1)) and risk_activity_situation_count > 0 and duration > 15:
        medium_level_close_contact_count += 1

    if risk_activity_situation_count > 0 and risk_spaces_count > 1:
        high_level_crowding_count += 1

    if risk_activity_situation_count > 0 and risk_spaces_count == 1:
        medium_level_crowding_count += 1

    if situation_types != None and risk_spaces_count > 0:
        high_level_closed_space_count += 1

    if situation_types != None and risk_spaces_count == 0:
        medium_level_closed_space_count += 1
    

print("generate %s test data." % data_count)

print("plod:HighLevelCloseContact count by generate_testdata.py: %s" % high_level_close_contact_count)
print("plod:MediumLevelCloseContact count by generate_testdata.py: %s" % medium_level_close_contact_count)
print("plod:HighLevelCrowding count by generate_testdata.py: %s" % high_level_crowding_count)
print("plod:MediumLevelCrowding count by generate_testdata.py: %s" % medium_level_crowding_count)
print("plod:HighLevelClosedSpace count by generate_testdata.py: %s" % high_level_closed_space_count)
print("plod:MediumLevelClosedSpace count by generate_testdata.py: %s" % medium_level_closed_space_count)


store.serialize("test.rdf", format="pretty-xml", max_depth=3)
