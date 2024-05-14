import os
import re
import csv
from tqdm import tqdm
import geopy.distance

from config import (
    LAT,
    LON,
    FOLDER_OUTPUT,
    SEPARATORS,
    SEPARATORS_LAN_LOT,
    SEPARATORS_LAN_LOT_TEXT,
    FOLDER_INPUT,
)


def _calculate_distance(coord: list, file_name: str) -> dict[list, str]:
    res = []
    for lat, lon in coord:
        distance = geopy.distance.geodesic([lat, lon], [LAT, LON]).km
        res.append(
            [
                lat,
                lon,
                distance,
                round(distance * 1000, 1),
            ]
        )
    if res:
        res.insert(
            0,
            [
                'Широта',
                'Довгота',
                'Відстань (км)',
                'Відстань (м)',
                # 'Статус',
            ],
        )
        with open(os.path.join(FOLDER_OUTPUT, file_name), 'w') as new_file:
            writer = csv.writer(
                new_file,
                delimiter='\t',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerows(res)


def _get_basic_coordinates() -> list:
    for file_take in tqdm(os.listdir(FOLDER_INPUT)):
        use_list = []
        with open(os.path.join(FOLDER_INPUT, file_take), 'r') as file_use:
            csv_list = []
            for sep in SEPARATORS:
                csv_list = [
                    [
                        k
                        for j
                        in i
                        if j and (k := j.strip())
                    ]
                    for i
                    in csv.reader(
                        file_use,
                        delimiter=sep
                    )
                ]
                if csv_list:
                    for i in csv_list:
                        use_list.extend(i)
                    break
        use_list = [
            i.replace('(', '').strip() if i.startswith('(') else i
            for i
            in use_list
        ]
        use_list = [
            i.replace(')', '').strip() if i.endswith(')') else i
            for i
            in use_list
        ]

        #DETECT SEPARATOR / WITHOUT SEPARATOR
        if any(
            any(
                sep in i
                for sep
                in SEPARATORS_LAN_LOT_TEXT
            )
            for i
            in use_list
        ):
            used = [
                i
                for i
                in use_list
                if any(
                    sep in i
                    for sep
                    in SEPARATORS_LAN_LOT_TEXT
                )
            ]
            for u in used:
                for sep in SEPARATORS_LAN_LOT_TEXT:
                    if not sep in u:
                        continue
                    v = u.split(sep)
                    for tst in v:
                        if not '.' in tst:
                            continue
                        if any(
                            len(tst.split(z)) == 2 and any(
                                k.replace('.', '').isdigit() 
                                for k
                                in tst.split(z)
                            )
                            for z
                            in SEPARATORS_LAN_LOT
                        ):
                            use_list.append(tst)
                        elif len([r for r in tst if r.isdigit()]) > 8 and not any(
                            len(tst.split(z)) == 2 and any(
                                k.replace('.', '').isdigit() 
                                for k
                                in tst.split(z)
                            )
                            for z
                            in SEPARATORS_LAN_LOT
                        ) and (m:=re.search(r"\d", tst)):
                            m = m.start()
                            use_list.append(tst[m:])
            use_list = [i for i in use_list if not i in used]

        value_indexes = [
            sorted(
                [
                    [
                        i, use.index(i),
                    ]
                    for i
                    in SEPARATORS_LAN_LOT
                    if i in use
                ],
                key = lambda x: x[1],
                reverse = False
            )
            for use in use_list
        ]
        value_indexes = [
            i[0][0]
            for i
            in value_indexes
        ]
        use_list = [
            [
                i.strip()
                for i
                in j.split(sep)
            ]
            for j, sep in zip(
                use_list,
                value_indexes,
            )
        ]
        use_list = [
            i
            for i
            in use_list
            if len(i) == 2 and any(k.replace('.', '').isdigit() for k in i)
        ]
        _calculate_distance(use_list, file_take)


if __name__ == '__main__':
    (
        os.path.exists(FOLDER_OUTPUT) or
        os.mkdir(FOLDER_OUTPUT)
    )
    _get_basic_coordinates()