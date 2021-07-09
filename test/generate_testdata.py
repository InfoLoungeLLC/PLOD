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
'''
from owlready2 import *
from rdflib import Graph, Literal, BNode, RDF, RDFS, Namespace, URIRef
from rdflib.namespace import XSD
import time
import random
import sys
import csv

args = sys.argv
data_count = int(args[1])

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
    p = dict(name=place[0].name, iri=place[0].iri, DropletReachableActivity=0)
    for afford in affords:
        if(hasattr(afford[1], 'iri') and afford[1].iri == 'http://plod.info/rdf/DropletReachableActivity'):
            p['DropletReachableActivity'] += 1
    place_samples.append(p)

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
        activity_samples.append(dict(name=activity[0].name, iri=activity[0].iri,
                                     isDropletReachableActivity=activity_type[0].iri == 'http://plod.info/rdf/DropletReachableActivity'))

risk_activity_situations = list(my_world.sparql("""
    %s
    SELECT DISTINCT * WHERE {
        ?s a plod:RiskActivitySituation .
    } limit 1000""" % (prefix)))

risk_activity_situation_samples = []
for risk_activity_situation in risk_activity_situations:
    s = dict(name=risk_activity_situation[0].name,
             iri=risk_activity_situation[0].iri)
    risk_activity_situation_samples.append(
        dict(name=risk_activity_situation[0].name, iri=risk_activity_situation[0].iri))

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

events = []
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

    uri = "http://plod.info/rdf/id/event_%s" % i
    event_uri = URIRef(uri)
    store.add((event_uri, RDF.type, schema.Event))
    store.add((event_uri, RDFS.label, Literal("event_%s" % i)))

    location = random.choice(place_samples)
    store.add((event_uri, schema.Location, URIRef(
        "http://plod.info/rdf/id/%s" % location['name'])))

    action_count = random.randint(0, 3)
    actions = random.sample(activity_samples, action_count)
    droplet_reachable_activity_count = 0
    for action in actions:
        store.add((event_uri, plod.action, URIRef(
            "http://plod.info/rdf/%s" % action['name'])))
        if(action["isDropletReachableActivity"]):
            droplet_reachable_activity_count += 1

    person_count = random.randint(1, 4)
    persons = random.sample(person_samples, person_count)
    for person in persons:
        store.add((event_uri, plod.agent, person))

    risk_activity_situation_count = random.randint(0, 2)
    risk_activity_situations = random.sample(
        risk_activity_situation_samples, risk_activity_situation_count)
    for risk_activity_situation in risk_activity_situations:
        store.add((event_uri, plod.situationOfActivity, URIRef(
            "http://plod.info/rdf/%s" % risk_activity_situation['name'])))

    time_uri = URIRef("http://plod.info/rdf/id/time_%s" % i)
    store.add((time_uri, RDF.type, time.Interval))
    store.add((event_uri, plod.time, time_uri))

    duration = random.randint(0, 30)
    time_temporal_duration_uri = URIRef(
        "http://plod.info/rdf/id/duration_%s" % i)
    store.add((time_temporal_duration_uri, RDF.type, time.TemporalDuration))
    store.add((time_uri, time.hasDuration, time_temporal_duration_uri))
    store.add((time_temporal_duration_uri, time.numericDuration,
               Literal(duration, datatype=XSD.decimal)))

    event = dict(uri=uri, iri=place[0].iri, locationHasOneMoreThanDropletReachableActivity=location['DropletReachableActivity'] > 1
                 > 1, eventHasOneMoreThanDropletReachableActivity=droplet_reachable_activity_count > 1, eventHasRiskActivitySituation=risk_activity_situation_count > 0, longerThan15=duration > 15)
    events.append(event)

high_level_close_contact_count = 0
for event in events:
    if((event["locationHasOneMoreThanDropletReachableActivity"] or event["eventHasOneMoreThanDropletReachableActivity"]) and event["eventHasRiskActivitySituation"] and event["longerThan15"]):
        high_level_close_contact_count += 1
print("generate %s test data." % data_count)
print("plod:HighLevelCloseContact count by generate_testdata.py: %s" % high_level_close_contact_count)

store.serialize("test.rdf", format="pretty-xml", max_depth=3)
