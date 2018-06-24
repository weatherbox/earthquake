import requests
import json
import re
import time
import csv


'''
最大震度
1996年9月以前 震度５、震度６
'''
MaxIntTable = {
    '１': 1,
    '２': 2,
    '３': 3,
    '４': 4,
    '５': 5,
    '５弱': 5,
    '５強': 6,
    '６': 7,
    '６弱': 7,
    '６強': 8,
    '７': 9
}

def main():
    with open('data.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['DateTime', 'Latitude', 'Longitude', 'Depth', 'Magnitude', 'MaxIntensity', 'MaxIntensityStr', 'Eqicenter', 'EventID'])

        latestID = 0
        rows = fetch('1923/01/01', '00:00')
        #rows = fetch('2018/01/01', '00:00')

        while rows and int(rows[-1][-1]) != latestID:
            for row in rows:
                if int(row[-1]) > latestID:
                    writer.writerow(row)

            # next
            latest = rows[-1]
            latestID = int(latest[-1])

            time.sleep(1)
            rows = fetch(latest[0][:10], latest[0][11:16])


def fetch(date, time):
    print(date, time)
    url = 'http://www.data.jma.go.jp/svd/eqdb/data/shindo/index.php'
    res = requests.post(url, {
        'ymdF': date,
        'hmsF': time,
        'ymdT': '2018/06/23',
        'hmsT': '23:59',
        'MaxI': 'I3',
        'MinM': 'F00',
        'MaxM': 'T95',
        'DepF': 0,
        'DepT': 999,
        'EpiN[]': 999,
        'Pref[]': 99,
        'City[]': 99999,
        'Obs[]': 9999999,
        'Int': 1,
        'Search': '',
        'Sort': 'S1',
        'Comp': 'C0',
        'DetailFlg': 0
    })
    res.encoding = 'utf-8'

    match = re.search(r"var hyp = \[(.*)\]", res.text)
    if match:
        hyp = match.group(1)
        lines = hyp.split(',')

        rows = []
        for line in lines:
            row = parse(line)
            if row: rows.append(row)
        rows.reverse()
        return rows


def parse(line):
    elems = line[1:-1].split('|')
    txts = elems[0].split('\u3000')

    time = txts[0]
    if len(time) == 16: time += ':00.0'
    elif len(time) == 19: time += '.0'
    magnitude = str(float(elems[4]) / 10) if elems[4] != '-99' else '-1'
    maxintstr = txts[4][4:]
    maxint = MaxIntTable[maxintstr]
    eventID = elems[1].split('=')[1]

    # DateTime, Latitude, Longitude, Depth, Magnitude, MaxIntensity, MaxIntensityStr, Eqicenter, EventID
    data = [time, elems[2], elems[3], elems[5], magnitude, maxint, maxintstr, txts[1], eventID]

    # invalid date format
    match = re.search(r"月", time)
    if match:
        print(data)
        return

    return data


if __name__ == '__main__':
    main()


