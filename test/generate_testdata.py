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
不可能な組み合わせ
h-h-m
h-m-m
h-l-h
m-h-m
m-m-m
m-l-h


l-h-m
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
    "../rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality.owl").load()
my_world.save()

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
    p = {'name': place[0].name, 'iri': place[0].iri,
         'droplet_reachable_activity': 0}
    for afford in affords:
        if(hasattr(afford[1], 'iri') and afford[1].iri == 'http://plod.info/rdf/DropletReachableActivity'):
            p['droplet_reachable_activity'] += 1
    place_samples.append(p)

activity_types = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a owl:Class ;
           rdfs:subClassOf+ plod:Activity .
    } limit 1000""" % (prefix)))

activity_samples = []
reachable_activity_samples = []
not_reachable_activity_samples = []
for activity_type in activity_types:
    activities = list(my_world.sparql("""
        %s
        SELECT DISTINCT * WHERE {
            ?s a <%s>
        } limit 1000""" % (prefix, activity_type[0].iri)))
    for activity in activities:
        sample = {'name': activity[0].name, 'iri': activity[0].iri,
                  'is_droplet_reachable_activity': activity_type[0].iri == 'http://plod.info/rdf/DropletReachableActivity'}
        activity_samples.append(sample)
        if sample["is_droplet_reachable_activity"]:
            reachable_activity_samples.append(sample)
        else:
            not_reachable_activity_samples.append(sample)


risk_activity_situations = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a plod:RiskActivitySituation .
    } limit 1000""" % (prefix)))

risk_activity_situation_samples = []
for risk_activity_situation in risk_activity_situations:
    risk_activity_situation_samples.append(
        {'name': risk_activity_situation[0].name, 'iri': risk_activity_situation[0].iri})


risk_spaces_situations = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a plod:RiskSpaceSituation .
    } limit 1000""" % (prefix)))

risk_spaces_situation_samples = []
for risk_spaces_situation in risk_spaces_situations:
    risk_spaces_situation_samples.append(
        {'name': risk_spaces_situation[0].name, 'iri': risk_spaces_situation[0].iri})


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

# situation_samples = []
# # print(situation_types)
# for situation_type in situation_types:
#     print(situation_type)
#     situations = list(my_world.sparql("""
#         %s
#         SELECT DISTINCT * WHERE {
#             ?s a <%s>
#         } limit 1000""" % (prefix, situation_type[0].iri)))
#     print(situations)
#     for situation in situations:
#         situation_samples.append({'name': situation[0].name, 'iri': situation[0].iri,
#                                      'isSituationOf': situation_type[0].iri == 'http://plod.info/rdf/isSituationOf'})
# # print(situation_samples)

store = Graph()
schema = Namespace("https://schema.org/")
time = Namespace("http://www.w3.org/2006/time#")

store.bind("schema", schema)
store.bind("time", time)

g = Graph()
g.parse("../rdf/PLOD_schema.owl", format="xml")
plod = Namespace("http://plod.info/rdf/")
store.bind("plod", plod)

for place_sample in place_samples:
    place_sample_uri = URIRef(
        "http://plod.info/rdf/id/%s" % place_sample['name'])
    store.add((place_sample_uri, RDFS.label, Literal(place_sample['name'])))
    store.add((place_sample_uri, RDF.type, URIRef(place_sample['iri'])))

person_samples = []
for i in range(data_count):
    person_sample_uri = URIRef(
        "http://plod.info/rdf/id/person_%s" % i)
    store.add((person_sample_uri, RDF.type, schema.Person))
    store.add((person_sample_uri, RDFS.label, Literal("person_%s" % i)))
    person_samples.append(person_sample_uri)

high_events = []
mid_events = []
low_events = []
for i in range(data_count):
    if i < first_count:
        close_contact_level = case[1]
        crowding_level = case[2]
        closed_space_level = case[3]
    elif i < first_count + second_count:
        close_contact_level = case[5]
        crowding_level = case[6]
        closed_space_level = case[7]
    else:
        close_contact_level = case[9]
        crowding_level = case[10]
        closed_space_level = case[11]

    # print(close_contact_level, crowding_level, closed_space_level)

    uri = "http://plod.info/rdf/id/event_%s" % i
    event_uri = URIRef(uri)
    store.add((event_uri, RDF.type, schema.Event))
    store.add((event_uri, RDFS.label, Literal("event_%s" % i)))

    location, actions = sl.location_and_action(
        close_contact_level, place_samples, reachable_activity_samples, not_reachable_activity_samples)

    store.add((event_uri, schema.Location, URIRef(
        "http://plod.info/rdf/id/%s" % location['name'])))

    droplet_reachable_activity_count = 0
    for action in actions:
        store.add((event_uri, plod.action, URIRef(
            "http://plod.info/rdf/%s" % action['name'])))
        if(action["is_droplet_reachable_activity"]):
            droplet_reachable_activity_count += 1

    person_count = random.randint(1, 4)
    persons = random.sample(person_samples, person_count)
    for person in persons:
        store.add((event_uri, plod.agent, person))

    risk_activity_situation_count, risk_activity_situations = sl.activity_situation(
        close_contact_level, risk_activity_situation_samples)

    for risk_activity_situation in risk_activity_situations:
        store.add((event_uri, plod.situationOfActivity, URIRef(
            "http://plod.info/rdf/%s" % risk_activity_situation['name'])))

    time_uri = URIRef("http://plod.info/rdf/id/time_%s" % i)
    store.add((time_uri, RDF.type, time.Interval))
    store.add((event_uri, plod.time, time_uri))

    duration = sl.random_duration(close_contact_level)

    time_temporal_duration_uri = URIRef(
        "http://plod.info/rdf/id/duration_%s" % i)
    store.add((time_temporal_duration_uri, RDF.type, time.TemporalDuration))
    store.add((time_uri, time.hasDuration, time_temporal_duration_uri))
    store.add((time_temporal_duration_uri, time.numericDuration,
               Literal(duration, datatype=XSD.decimal)))

    # sl.space_situation(crowding_level, risk_spaces_situation_samples)

    high_event = {'uri': uri, 'iri': place[0].iri, 'location_has_one_more_than_droplet_reachable_activity': location['droplet_reachable_activity'] > 1,
                  'event_has_one_more_than_droplet_reachable_activity': droplet_reachable_activity_count > 1, 'event_has_one_risk_activity_situation': risk_activity_situation_count > 0, 'longer_than_15': duration > 15}
    high_events.append(high_event)

    mid_event = {'uri': uri, 'iri': place[0].iri, 'location_has_one_more_than_droplet_reachable_activity': location['droplet_reachable_activity'] == 1 and droplet_reachable_activity_count <= 1,
                 'event_has_one_more_than_droplet_reachable_activity': droplet_reachable_activity_count == 1 and location['droplet_reachable_activity'] <= 1, 'event_has_one_risk_activity_situation': risk_activity_situation_count > 0, 'longer_than_15': duration > 15}
    mid_events.append(mid_event)

    low_event = {'uri': uri, 'iri': place[0].iri, 'location_has_one_more_than_droplet_reachable_activity': location['droplet_reachable_activity'] == 0,
                 'event_has_one_more_than_droplet_reachable_activity': droplet_reachable_activity_count == 0, 'event_has_one_risk_activity_situation': risk_activity_situation_count == 0, 'longer_than_15': duration <= 15}
    low_events.append(low_event)

print("generate %s test data." % data_count)

high_level_close_contact_count = 0
for event in high_events:
    if((event["location_has_one_more_than_droplet_reachable_activity"] or event["event_has_one_more_than_droplet_reachable_activity"]) and event["event_has_one_risk_activity_situation"] and event["longer_than_15"]):
        high_level_close_contact_count += 1
print("plod:HighLevelCloseContact count by generate_testdata.py: %s" %
      high_level_close_contact_count)

high_level_close_contact_count = 0
for event in mid_events:
    if((event["location_has_one_more_than_droplet_reachable_activity"] or event["event_has_one_more_than_droplet_reachable_activity"]) and event["event_has_one_risk_activity_situation"] and event["longer_than_15"]):
        high_level_close_contact_count += 1
print("plod:MiddleLevelCloseContact count by generate_testdata.py: %s" %
      high_level_close_contact_count)

high_level_close_contact_count = 0
for event in low_events:
    if((event["location_has_one_more_than_droplet_reachable_activity"] and event["event_has_one_more_than_droplet_reachable_activity"]) and event["event_has_one_risk_activity_situation"] and event["longer_than_15"]):
        high_level_close_contact_count += 1
print("plod:LowLevelCloseContact count by generate_testdata.py: %s" %
      high_level_close_contact_count)

store.serialize("test.rdf", format="pretty-xml", max_depth=3)
