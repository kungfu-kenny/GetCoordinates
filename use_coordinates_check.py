"""
Формат данных WGS 84 (YX, Google). Проверку можно делать на Донецкой обл. 
 
 1. Обычные координаты, обычный csv
 
 широта: 2 цифры - точка 5-6 цифр
 долгота: 2 цифры - точка 5-6 цифр
 
 разделитель целой и дробной части - точка 
 разделитель между широтой и долготой - запятая (пробелы могут быть или отсутствовать)
 разделитель между координатами - точка с запятой
 
 Например:
 11.123456, 22.123456; 33.123456, 44.123456;
 
 2. Координаты с пробелами, обычный csv  
 
 разделитель целой и дробной части - точка 
 разделитель между широтой и долготой - пробел (один или несколько)
 разделитель между координатами - точка с запятой 
 
 Например:
 11.123456 22.123456; 33.123456 44.123456;

 3. Аналогично п.1, п.2, но могут попадаться текстовые комментарии комментарии 
 
 Например:
 11.123456 22.123456; парковка каких-то бедолаг; 33.123456 44.123456;
 
 4. Кривые руки оператора и вариации на тему
 
 разделитель между целой и дробной частью - точка
 разделитель между широтой и долготой - точка (!), возможно с пробелами
 разделитель между координатами - точка с запятой

 11.123456. 22.123456; 33.123456. 44.123456; 

 5. Массив с комментариями после
 
 разделители как в п.1-4, только по одной паре координат на строку, затем комментарий и новая строка
 разделитель между координатами и текстовой частью может быть (чаще всего это тире) или отсутствовать

 Например: 
 11.123456, 22.123456 - описание кто из наших попадает под раздачу и тд
 33.123456, 44.123456 - описание еще чего-то 
 55.123456, 66.123456 - и еще какой- то комментарий 
 
 6. Массив с комментариями перед
 
 Аналогично п.5 только комментарий перед координатами (или что чаще бывает - название нас. пункта) 
 
 Железный порт - 11.123456, 22.123456 
 Какое-то описание что там находится 33.123456, 44.123456
 
 7. Варианты со скобками (когда массив координат под нас. пункт обрамляется), например:
 
 (11.123456, 22.123456; 33.123456, 44.123456; 55.123456, 66.123456)
"""
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