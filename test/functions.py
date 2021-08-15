from owlready2 import *
from rdflib import Graph, Literal, BNode, RDF, RDFS, Namespace, URIRef
from rdflib.namespace import XSD
import random
import time
import csv


def select_location_and_actions(levels, samples):
    if levels['close_contact'] == "HighLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)

        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(
                filter(lambda place: place['droplet_reachable_activity'] > 1, samples['place']))
            droplet_reachable_count = random.randint(0, 1)

        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(
                filter(lambda place: place['droplet_reachable_activity'] < 2, samples['place']))
            droplet_reachable_count = random.randint(2, 3)

        else:
            # 両方の条件を満たす
            filter_samples = list(
                filter(lambda place: place['droplet_reachable_activity'] > 1, samples['place']))
            droplet_reachable_count = random.randint(2, 3)

    elif levels['close_contact'] == "MediumLevelCloseContact":
        # 0の時の条件が上手く検出されない
        use_condition = random.randint(0, 2)

        if use_condition == 0:
            # 1の条件のみを満たす
            filter_samples = list(filter(
                lambda place: place['droplet_reachable_activity'] == 1, samples['place']))
            droplet_reachable_count = 0

        elif use_condition == 1:
            # 2の条件のみを満たす
            filter_samples = list(filter(
                lambda place: place['droplet_reachable_activity'] == 0, samples['place']))
            droplet_reachable_count = 1

        else:
            # 両方の条件を満たす
            filter_samples = list(filter(
                lambda place: place['droplet_reachable_activity'] == 1, samples['place']))
            droplet_reachable_count = 1

    else:
        # LowLevelCloseContactのとき
        filter_samples = list(filter(
            lambda place: place['droplet_reachable_activity'] == 0, samples['place']))
        droplet_reachable_count = 0

    not_droplet_reachable_count = random.randint(
        0, 3 - droplet_reachable_count)
    location = random.choice(filter_samples)
    droplet_reachable_actions = random.sample(
        samples['reachable_activity'], droplet_reachable_count)
    not_droplet_reachable_actions = random.sample(
        samples['not_reachable_activity'], not_droplet_reachable_count)
    actions = droplet_reachable_actions + not_droplet_reachable_actions
    return location, actions


def select_select_activity_situation(levels, risk_activity_situation_samples):
    if levels['close_contact'] == "HighLevelCloseContact" or levels['close_contact'] == "MediumLevelCloseContact" or levels['crowding'] == "HighLevelCrowding" or levels['crowding'] == "MediumLevelCrowding":
        risk_activity_situation_count = random.randint(1, 2)
    else:
        risk_activity_situation_count = 0

    risk_activity_situations = random.sample(
        risk_activity_situation_samples, risk_activity_situation_count)
    return risk_activity_situation_count, risk_activity_situations


def random_duration(levels):
    if levels['close_contact'] == "HighLevelCloseContact" or levels['close_contact'] == "MediumLevelCloseContact":
        return random.randint(16, 30)
    else:
        return random.randint(0, 15)


def select_space_situation(levels, risk_spaces_situation_samples):
    if levels['crowding'] == "HighLevelCrowding":
        # 中身が2種類しかないのでそのまま返す
        return risk_spaces_situation_samples

    elif levels['crowding'] == "MediumLevelCrowding":
        risk_spaces_situations = random.choice(risk_spaces_situation_samples)
        return [risk_spaces_situations]

    elif levels['closed_space'] == "HighLevelClosedSpace":
        risk_spaces_situations = random.choice(risk_spaces_situation_samples)
        return [risk_spaces_situations]


def select_situation_type(levels, situation_samples):
    situation = None
    if levels['closed_space'] == "HighLevelClosedSpace" or levels['closed_space'] == "MediumLevelClosedSpace":
        situation = random.choice(situation_samples)
    return situation


def generate_testdata(data_count=100, case_number=1):
    # read CSV
    with open('sample.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        case_sample = [row for row in reader]

    case = case_sample[case_number]

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
        store.add((place_sample_uri, RDFS.label,
                   Literal(place_sample['name'])))
        store.add((place_sample_uri, RDF.type, URIRef(place_sample['iri'])))

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

        location, actions = select_location_and_actions(levels, samples)

        location_uri = URIRef("http://plod.info/rdf/%s_%s" %
                              (location['name'], i))
        location_uri_noindex = URIRef(
            "http://plod.info/rdf/%s" % location['name'])
        store.add((event_uri, schema.location, location_uri))
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

        time_uri = URIRef("http://plod.info/rdf/id/time_%s" % i)
        store.add((time_uri, RDF.type, time.Interval))
        store.add((event_uri, plod.time, time_uri))

        duration = random_duration(levels)

        time_temporal_duration_uri = URIRef(
            "http://plod.info/rdf/id/duration_%s" % i)
        store.add((time_temporal_duration_uri, RDF.type, time.TemporalDuration))
        store.add((time_uri, time.hasDuration, time_temporal_duration_uri))
        store.add((time_temporal_duration_uri, time.numericDuration,
                   Literal(duration, datatype=XSD.decimal)))

        situation = select_situation_type(levels, samples['situation_type'])
        if situation != None:
            situation_uri = URIRef("http://plod.info/rdf/id/situation_%s" % i)
            store.add((situation_uri, RDF.type, plod.Situation))
            store.add((situation_uri, plod.isSituationOf, URIRef(
                "http://plod.info/rdf/%s" % situation['name'])))

        risk_activity_situation_count, risk_activity_situations = select_select_activity_situation(
            levels, samples['risk_activity_situation'])

        for risk_activity_situation in risk_activity_situations:
            store.add((event_uri, plod.situationOfActivity, URIRef(
                "http://plod.info/rdf/%s" % risk_activity_situation['name'])))
            store.add((situation_uri, plod.situationOfActivity, URIRef(
                "http://plod.info/rdf/%s" % risk_activity_situation['name'])))

        risk_spaces = select_space_situation(
            levels, samples['risk_space_situation'])
        risk_spaces_count = 0
        if risk_spaces != None:
            for risk_space in risk_spaces:
                risk_spaces_count += 1
                store.add((situation_uri, plod.situationOfSpace, URIRef(
                    "http://plod.info/rdf/%s" % risk_space['name'])))

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

    print("plod:HighLevelCloseContact count by generate_testdata.py: %s" %
          high_level_close_contact_count)
    print("plod:HighLevelClosedSpace count by generate_testdata.py: %s" %
          high_level_closed_space_count)
    print("plod:HighLevelCrowding count by generate_testdata.py: %s" %
          high_level_crowding_count)
    print("plod:MediumLevelCrowding count by generate_testdata.py: %s" %
          medium_level_crowding_count)
    print("plod:MediumLevelClosedSpace count by generate_testdata.py: %s" %
          medium_level_closed_space_count)
    print("plod:MediumLevelCrowding count by generate_testdata.py: %s" %
          medium_level_crowding_count)

    store.serialize("""rdf/test_%s_%s.rdf""" % (case_number, data_count), format="pretty-xml", max_depth=3)

    return [high_level_close_contact_count, high_level_closed_space_count, high_level_crowding_count, medium_level_crowding_count, medium_level_closed_space_count, medium_level_crowding_count]

def reasoning(data_count=100, case_number=1):
    start_time = time.time()

    my_world = World(filename="./reasoning.sqlite")
    my_world = World()
    onto = my_world.get_ontology(
        "../rdf/SARS-CoV-2_Infection_Risk_Ontology_cardinality_ExactlyToMin.owl").load()
    data = my_world.get_ontology("""rdf/test_%s_%s.rdf""" % (case_number, data_count)).load()
    sync_reasoner([onto, data])
    my_world.save()

    types = ['HighLevelCloseContact', 'HighLevelClosedSpace', 'HighLevelCrowding',
             'MediumLevelCloseContact', 'MediumLevelClosedSpace', 'MediumLevelCrowding']
    counts = []

    for t in types:
        results = list(my_world.sparql("""
        PREFIX plod: <http://plod.info/rdf/>
        SELECT DISTINCT * WHERE {
            ?s rdf:type plod:%s .
        } limit 1000""" % t))
        ids = []
        for result in results:
            ids.append(result[0].iri)
        # ids.sort()
        # print(ids)
        counts.append(len(ids))
        print("plod:%s count by reasoning.py: %s" % (t, len(ids)))

    counts.append(time.time() - start_time)
    print("--- %s seconds ---" % (time.time() - start_time))
    return counts
