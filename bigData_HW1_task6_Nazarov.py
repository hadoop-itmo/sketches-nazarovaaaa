#   Описание алгоритма:
#   1.Прохожусь по файлу 1
#   1.1.Подсчитываю в Counter точное число ключей (пока не превысили 1.000.000)
#   1.2.Параллельно веду Count-Min Sketch (для подсчета примерной встречаемости)
#   1.3.Также заведу BloomFilter (идею описал в п.2.3)
#   2.Прохожусь по файлу 2
#   2.1.Если в Counter1 < 1.000.000, веду Counter и для 2 файла
#   2.2.Параллельно веду неточный подсчет, обращаясь в Count-Min Sketch из п.1.2
#   2.3.Существует риск, когда из-за одинакового хэша ключи, которых не было в файле 1
#   могут внести лишний вклад в подсчет - для этого можно предварительно "отсеивать"
#   их с помощью BloomFilter из п.1.3
#   По итогу понадобится ровно 1 проход по каждому из файлов

#   Описание структур данных:
#   1.Предлагаю в качестве размера BloomFilter взять N = 100.000.000 * 10,
#   поскольку в файле может быть до 100.000.000 уникальных ключей.
#   Тогда оптимальное число хэш-функций будет k = N / n * ln(2)=10 * ln(2) ~ 7
#   В таком случае вероятность ложного срабатывания по исходной формуле будет составлять
#   P = (1 - (1 - 1 / N) ^ (k * n)) ^ k ~ 0.0082, что составляет 0.8 %.
#   Чтобы учитывать все возможные уже реализованные оптимизации для ускорения работы,
#   буду использовать BloomFilter из пакета bloom-filter (можно использовать из задания 2)
#   2.В качестве размера Count-Min Sketch предлагаю взять w = [e/0.000001] ~ 2 718 281,
#   а глубины d = [ln(1/0.01)] = 4, в таком случае оценка вхождений элемента
#   с вероятностью как минимум 1-0.01 = 0.99, что составляет 99%, будет в промежутке
#   от реального значения до реального значения * 1.000001

import numpy as np
from collections import Counter
import csv
import mmh3
from bloom_filter import BloomFilter


def CountJoinSize(filename1, filename2, max_keys=1000000, max_size_join=10000000):
    #   завожу Counter для точного подсчета числа вхождений различных ключей в файлы
    c1, c2 = Counter(), Counter()
    #   завожу структуру Min-Sketch (заполняю нулями)
    d = 4
    w = 2718281
    Count_Min = np.zeros((d, w))
    #   завожу BloomFilter из пакета (указываю размер и сразу рассчитанный процент ошибки)
    Bloom = BloomFilter(max_elements=1000000000, error_rate=0.0082)
    #   true, пока используем точный подсчет
    accCalc = True
    #   веду для подсчета
    calc2 = 0  # неточного
    calc1 = 0  # точного
    #   обхожу 1ый файл
    with open(filename1, 'r') as csvfile1:
        csvreader1 = csv.reader(csvfile1)
        for row in csvreader1:
            #   заполняю Count-Min Sketch
            for i in range(d):
                pos = mmh3.hash(row[0], i) % w
                Count_Min[i][pos] += 1
            #   заполняю Bloom
            Bloom.add(row[0])
            #   пока использую точный подсчет - веду Counter
            if accCalc is True:
                if len(c1) >= max_keys:
                    #   перехожу на неточный подсчет
                    accCalc = False
                    #   сразу могу очистить Counter
                    c1.clear()
                #   иначе добавляю ключ в Counter
                elif row[0] not in c1:
                    c1[row[0]] = 1
                else:
                    c1[row[0]] += 1
    csvfile1.close()

    #   реализую проход по второму файлу
    with open(filename2, 'r') as csvfile2:
        csvreader2 = csv.reader(csvfile2)
        for row in csvreader2:
            #   если ключ не входит в блум-фильтр, значит такого ключа не было - пропускаем
            if row[0] in Bloom:
                temp_min_count = float('inf')
                #   если не очищал Counter1, могу получить точное значение
                if accCalc is True and row[0] in c1:
                    calc2 += c1[row[0]]
                #   иначе проверяю на вхождение в Count_min
                else:
                    for i in range(d):
                        pos = mmh3.hash(row[0], i) % w
                        if Count_Min[i][pos] < temp_min_count:
                            temp_min_count = Count_Min[i][pos]
                    #   накапливаю неточную оценку
                    calc2 += temp_min_count

        #   если еще используем точный подсчет, то веду Counter
        if accCalc is True:
            #   если вышли за 1.000.000, меняю флаг и очищаю
            if len(c2) >= max_keys:
                accCalc = False
                c2.clear()
            #   иначе добавляю в Counter
            elif row[0] not in c2:
                c2[row[0]] = 1
            else:
                c2[row[0]] += 1
    csvfile2.close()

    #   если используем точный подсчет, то работаю с Counter'ами
    if accCalc is True:
        #   если ключ присутствует в обоих, перемножаю значения
        for key in c1:
            if key in c2:
                calc1 += c1[key] * c2[key]
                #   если превысили 10.000.000, перехожу на неточный подсчет
                if calc1 > max_size_join:
                    accCalc = False
                    break

    if accCalc is True:
        return calc1
    else:
        return calc2


# протестировал на:
# 1:
#   gen_grouped_seq("hw1_task6_test2_csv1.csv", [(10, 100000)])
#   gen_grouped_seq("hw1_task6_test2_csv2.csv", [(10, 100000)])
#   print(CountJoinSize("hw1_task6_test2_csv1.csv", "hw1_task6_test2_csv2.csv", 100, 1000))
# ожидаемо получил 0 (ключи между файлами уникальны)
# 2:
#   print(CountJoinSize("hw1_task6_test2_csv1.csv", "hw1_task6_test2_csv1.csv", 100, 1000))
# ожидаемо получил 100.000 * 100.000 * 10 (10 групп по 100.000 одинаковых ключей между файлами)
# 3:
#   gen_grouped_seq("hw1_task6_test3_csv1.csv", [(1000000, 1)])
#   print(CountJoinSize("hw1_task6_test3_csv1.csv", "hw1_task6_test3_csv1.csv", 100, 1000))
# свалился на неточный расчет и получил 1008871 вместо 1.000.000 (по одной паре совпадающих ключей)

