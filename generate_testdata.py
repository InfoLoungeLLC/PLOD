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
- schema:Placeを継承するクラスを再帰的に抽出してschema:locationの候補を取得
    - それぞれがplod:DropletReachableActivityを2つ以上持つかを判定しておく
- plod:Activityを継承するクラスを再帰的に抽出してschema:actionの候補を取得
    - それぞれがplod:DropletReachableActivity型かを判定しておく
- plod:RiskActivitySituation型のクラスを抽出してplod:situationOfActivityの候補を取得

### テストデータ生成
- schema:locationの候補となるクラスのダミーインスタンスを1つずつ生成
```
  <plod:Dummy rdf:about="http://plod.info/rdf/id/{xxx}}">
    <rdf:type rdf:resource="http://plod.info/rdf/{xxx}"/>
  </plod:Dummy>
```
- schema:Eventを作成し、rdf:about="http://plod.info/rdf/id/event_{xxx}"で一意となるURIを生成
- schema:locationプロパティから上述のダミーインスタンスを参照する。plod:DropletReachableActivityを2つ以上持つかの判定を内部保持
- plod:timeのダミーインスタンスを
```
  <time:Interval rdf:about="http://plod.info/rdf/id/time_{xxx}">
    <time:hasBeginning rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">{ISO 8601}</time:hasBeginning>
    <time:hasDuration>
      <time:TemporalDuration rdf:about="http://plod.info/rdf/id/duration_a42">
        <rdfs:label>duration_a42</rdfs:label>
        <time:numericDuration rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">{decimal}</time:numericDuration>
      </time:TemporalDuration>
    </time:hasDuration>

    <time:hasEnd rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">{ISO 8601}</time:hasEnd>
  </time:Interval>
```
の形式で生成し、schema:Eventのplod:timeプロパティで参照。15分以上(900秒以上）かどうかの判定を内部保持

- plod:agentを`<plod:agent rdf:resource="http://plod.info/rdf/id/person_{xxx}"/>`の形式でテストプロパティを適当な数生成
- plod:actionを任意の数生成。含まれるplod:DropletReachableActivity型の種類が2以上かどうかを判定して内部保持
- plod:situationOfActivityを任意の数生成。含まれるplod:RiskActivitySituation型の種類が2以上かどうかを判定して内部保持
- 生成が完了したら、そのschema:Eventがplod:HighLevelCloseContactかどうかを判定。例えば100個テストデータを生成した後、そのうちいくつがplod:HighLevelCloseContactになるはずかをコメント等で出力する
'''
#!/usr/bin/python
from owlready2 import *
from rdflib import Graph, Literal, BNode, RDF, RDFS, Namespace, URIRef
import time
import random

my_world = World()
my_world.set_backend(filename="./test.sqlite")
onto = my_world.get_ontology(
    "rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality.owl").load()
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
# print(place_samples)

# activity_types = list(my_world.sparql("""
#     %s
#     SELECT DISTINCT * WHERE {
#         ?s a owl:Class ;
#            rdfs:subClassOf+ plod:Activity .
#     } limit 1000""" % (prefix)))

# activity_samples = []
# for activity_type in activity_types:
#     activities = list(my_world.sparql("""
#         %s
#         SELECT DISTINCT * WHERE {
#             ?s a <%s>
#         } limit 1000""" % (prefix, activity_type[0].iri)))
#     for activity in activities:
#         activity_samples.append(dict(name=activity[0].name, iri=activity[0].iri, isDropletReachableActivity=activity_type[0].iri == 'http://plod.info/rdf/DropletReachableActivity'))
# print(activity_samples)

# risk_activity_situations = list(my_world.sparql("""
#     %s
#     SELECT DISTINCT * WHERE {
#         ?s a plod:RiskActivitySituation .
#     } limit 1000""" % (prefix)))

# risk_activity_situations_samples = []
# for risk_activity_situation in risk_activity_situations:
#     s = dict(name=risk_activity_situation[0].name, iri=risk_activity_situation[0].iri)
#     risk_activity_situations_samples.append(dict(name=risk_activity_situation[0].name, iri=risk_activity_situation[0].iri))
# print(risk_activity_situations_samples)

store = Graph()
schema = Namespace("https://schema.org/")

# Bind a few prefix, namespace pairs for pretty output
store.bind("schema", schema)

g = Graph()
g.parse("rdf/PLOD_schema.owl", format="xml")
plod = Namespace("http://plod.info/rdf/")
store.bind("plod", plod)

for place_sample in place_samples:
  place_sample_uri = URIRef("http://plod.info/rdf/id/%s" % place_sample['name'])
  store.add((place_sample_uri, RDF.type, schema.Place))
  store.add((place_sample_uri, RDFS.label, Literal(place_sample['name'])))
  store.add((place_sample_uri, RDF.type, URIRef(place_sample['iri'])))

events = []
for i in range(100):
  uri = "http://plod.info/rdf/id/event_%s" % i
  event_uri = URIRef(uri)
  store.add((event_uri, RDF.type, schema.Event))
  store.add((event_uri, RDFS.label, Literal("event_%s" % i)))
  location = random.choice(place_samples)
  store.set((event_uri, schema.Location, URIRef("http://plod.info/rdf/id/%s" % location['name'])))
  event = dict(uri=uri, iri=place[0].iri, isHighLevelCloseContact=False)
  events.append(event)

# print("--- printing raw triples ---")
# for s, p, o in store:
#     print(s, p, o)

# Serialize the store as RDF/XML to the file donna_foaf.rdf.
store.serialize("test.rdf", format="pretty-xml", max_depth=3)
