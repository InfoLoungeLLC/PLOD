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
import argparse
import functions as fc
import subprocess
import csv

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

parser = argparse.ArgumentParser()
parser.add_argument("--noDuration", help="optional", action="store_true")
args = parser.parse_args()

file = open("test_cases.csv")
reader = csv.reader(file)
case_counts = len(list(reader)) - 1

# data_counts_pattern = [100, 200, 500]
data_counts_pattern = [100, 200]

with open('./results.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['テストケース番号', 'テストデータ数',
                     'Generated HighLevelCloseContact',
                     'Generated HighLevelClosedSpace',
                     'Generated HighLevelCrowding',
                     'Generated MediumLevelCloseContact',
                     'Generated MediumLevelClosedSpace',
                     'Generated MediumLevelCrowding',
                     'Reasoned HighLevelCloseContact',
                     'Reasoned HighLevelClosedSpace',
                     'Reasoned HighLevelCrowding',
                     'Reasoned MediumLevelCloseContact',
                     'Reasoned MediumLevelClosedSpace',
                     'Reasoned MediumLevelCrowding',
                     '処理時間[秒]'])
    case_number = 1
    # while case_number < 3:
    while case_number < case_counts:
        for data_count in data_counts_pattern:
            result1 = fc.generate_testdata(case_number, data_count, args.noDuration)
            subprocess.Popen("""./monitor_memory.sh %s %s""" %
                            (case_number, data_count), shell=True)
            result2 = fc.reasoning(case_number, data_count, args.noDuration)
            writer.writerow([case_number, data_count] + result1 + result2)
            case_number += 1
