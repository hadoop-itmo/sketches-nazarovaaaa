import csv #для работы с csv-файлами
import math #для вычисления числа счетчиков
from collections import Counter #для реализации HeavyHitters

#сделаю решение универсальным по количеству строк в файле и частоте встречаемости
#по умолчанию значение будет, как в условии - 10.000.000.000 и 60.000
def CountProblemKeys(filename1, filename2, file_len = 10000000000, freq = 60000):

  #рассчитываю число счетчиков в зависимости от входных условий
  counters = math.ceil(file_len / freq)
  #шаг 1 - первый проход первого файла
  #реализация HeavyHitters
  p, c = None, Counter()
  with open(filename1, 'r') as csvfile1:
    csvreader = csv.reader(csvfile1)
    for row in csvreader:
      #работаю только с первой колонкой
      #если элемент есть, увеличиваю счетчик на 1
      if row[0] in c:
        c[row[0]] += 1
      #если элемента еще нет, но словарь не заполнен,
      #добавляю новый элемент
      elif (row[0] not in c) and (len(c) < counters):
        c[row[0]] = 1
      #если элемента нет, и словарь заполнен,
      #уменьшаю все счетчики на 1
      else:
        for i in list(c.keys()):
          c[i] -= 1
          #если счетчик обнулился, освобождаем
          if c[i] == 0:
            del c[i]
  csvfile1.close()
  #если ни один элемент не является подозреваемым, сразу выводим ответ
  if len(c) == 0:
    return c.keys()

  #шаг 2 - первый проход по второму файлу
  #подсчет числа вхождений "подозреваемых" из первого файла во второй
  #предварительно обнуляю все счетчики, так как подсчет будет новый
  for i in c.keys():
    c[i] = 0
  with open(filename2, 'r') as csvfile2:
    csvreader = csv.reader(csvfile2)
    for row in csvreader:
      if row[0] in c:
        c[row[0]] += 1
  #оставляю в словаре только те элементы, которые входят во второй файл 60.000+
  for i in list(c.keys()):
    if c[i] < freq:
      del c[i]
  csvfile2.close()
  #если ни один элемент из п.1 не входит во второй файл 60.000+, сразу даем ответ
  if len(c) == 0:
    return c.keys()

  #шаг 3 - второй проход по первому файлу
  #из оставшихся элементов из п.2 подсчитываю их точное число в первом файле
  for i in c.keys():
    c[i]=0
  with open(filename1, 'r') as csvfile1:
    csvreader = csv.reader(csvfile1)
    for row in csvreader:
      if row[0] in c:
        c[row[0]] += 1
  csvfile1.close()
  #исключаю оставшиеся "ложноположительные" элементы
  for i in list(c.keys()):
    if c[i] < freq:
      del c[i]
  #так как в условии явно не указан формат ответа,
  #верну список ключей с вхождением 60.000+ в оба файла
  return c.keys()