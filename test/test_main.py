#!/usr/bin/python
import argparse
import functions as fc
import subprocess
import csv

parser = argparse.ArgumentParser()
parser.add_argument("--noDuration", help="optional", action="store_true")
args = parser.parse_args()

file = open("test_cases.csv")
reader = csv.reader(file)
case_counts = len(list(reader)) - 1

data_counts_pattern = [100, 500, 1000]

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
    while case_number < case_counts:
        for data_count in data_counts_pattern:
            result1 = fc.generate_testdata(case_number, data_count, args.noDuration)
            subprocess.Popen("""./monitor_memory.sh %s %s""" %
                            (case_number, data_count), shell=True)
            result2 = fc.reasoning(case_number, data_count, args.noDuration)
            writer.writerow([case_number, data_count] + result1 + result2)
            case_number += 1
