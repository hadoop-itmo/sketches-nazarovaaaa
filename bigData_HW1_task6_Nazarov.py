import math #для вычисления вспомогательных мат. функций
import mmh3 # для вычисления хэша
from scipy.integrate import quad #для вычисления интеграла в HyperLogLog (предварительно нужно загрузить scipy)
import csv #для работы с csv-файлами

class HyperLogLogModify:#реализацию модифицированный класс HyperLogLog для реализации merge

  def __init__(self, b):
    self.b = b
    self.m = 1 << b
    self.M = []
    for i in range(self.m):
      self.M.append(0)

  #для реализации merge
  def __iter__(self):
    return iter(self.M)
  def __len__(self):
    return self.m
  def __setitem__(self, i, value):
    self.M[i] = value
  def __getitem__(self, i):
    return self.M[i]

  def put(self, s):
    x = mmh3.hash(s, signed = False)
    x = bin(x)[2:].zfill(32)
    j = int(x[:self.b], 2)
    w = x[self.b:]
    r = 1
    find_elem = False
    for i in w:
      if i == '1':
        find_elem = True
        break
      r += 1
    if find_elem == False:
      r += 1
    self.M[j] = max(self.M[j], r)

  def est_size(self):
    z = 0.0
    for j in range(self.m):
      z += 2 ** (-self.M[j])
    Z = z ** (-1)
    if self.m < 128:
      def integrand(x):
        return math.log2((2+x)/(1+x)) ** self.m
      alpha_m = (self.m * quad(integrand, 0, float('+inf'))[0]) ** (-1)
    else:
      alpha_m = 0.7213 / (1 + 1.079 / self.m)
    E = alpha_m * self.m ** 2 * Z
    if E <= 2.5 * self.m:
      V = 0
      for i in range(self.m):
        if self.M[i] == 0:
          V += 1
      if V > 0:
        E = self.m * math.log(self.m / V)
    elif E > (1.0 / 30.0) * (1 << 32):
      E = - (1 << 32) * math.log(1 - E / (2 << 32))

    return E

def merge(HLL1, HLL2):#реализация оценки объединения множеств
  max_len = max(len(HLL1), len(HLL2))
  HLL = HyperLogLogModify(int(math.log2(max_len)))
  for i in range(max_len):
    hll1_reg_i = HLL1[i]
    hll2_reg_i = HLL2[i]
    HLL[i] = max(hll1_reg_i, hll2_reg_i)

  return HLL

def CountJoinSize(filename1, filename2, max_keys = 1000000, max_size_join = 10000000):
  c1, c2 = set(), set()
  #true, если используем точный подсчет
  accCalc = True
  HLL1, HLL2 = HyperLogLogModify(10), HyperLogLogModify(10)
  len1, len2 = 0, 0
  #реализую проход по первому файлу
  with open(filename1, 'r') as csvfile1:
    csvreader1 = csv.reader(csvfile1)
    for row in csvreader1:
      HLL1.put(row[0])
      if accCalc == True:
        #если число ключей добралось до миллиона, заканчиваем точный подсчет
        if len(c1) >= max_keys:
          #переходим на оценку
          accCalc = False
          #очищаем множество
          c1.clear()
        #если текущей ключ уникален, то добавляю в set
        elif row[0] not in c1:
          c1.add(row[0])
  csvfile1.close()
  #реализую проход по второму файлу
  with open(filename2, 'r') as csvfile2:
    csvreader2 = csv.reader(csvfile2)
    for row in csvreader2:
      HLL2.put(row[0])
      if accCalc == True:
        if len(c2) >= max_keys:
          accCalc = False
          c2.clear()
        elif row[0] not in c2:
          c2.add(row[0])
  csvfile2.close()
  answer = 0
  if accCalc == True:
    answer = len(c1 & c2)
    return answer
  #если до сюда дошли, значит - точный подсчет не нужен
  #выполняю merge и подсчитываю с помощью операций с множествами
  #в случае, когда для первого файла заполнены set, буду использовать точное число вместо HLL
  P1, P2 = 0, 0
  if (len(c1) < max_keys and len(c1) > 0):
    P1 = len(c1)
  else:
    P1 = HLL1.est_size()
  answer = P1 + HLL2.est_size() - merge(HLL1, HLL2).est_size()
  return answer
