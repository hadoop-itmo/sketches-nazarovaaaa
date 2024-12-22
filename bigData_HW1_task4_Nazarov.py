import mmh3 #для вычисления хэша
import math #для вычисления вспомогательных мат. функций
from scipy.integrate import quad #для вычисления интеграла в HyperLogLog (предварительно нужно загрузить scipy)
class HyperLogLog:
  def __init__(self, b):
    #в классической реализации из статьи на вход подается 1 параметр - точность b
    #в зависимости от значения вычисляется число регистров
    #также используется 1 хэш-функция, а вероятность коллизий снижается за счет среднего гармонического между регистрами с нормировкой
    self.b = b
    self.m = 1 << b
    self.M = []
    for i in range(self.m):
      self.M.append(0)

  def put(self, s):
    #для общности буду брать только положительные значения (чтобы не завязываться на ведущий -)
    x = mmh3.hash(s, signed = False)
    #[2: из-за того, что битовая строка начинается с 0b
    x = bin(x)[2:].zfill(32)
    j = int(x[:self.b], 2)
    w = x[self.b:]
    r = 1
    #флаг для определения, нашли ли хоть одну ведущую единицу
    find_elem = False
    for i in w:
      if i == '1':
        find_elem = True
        break
      r += 1
    #если получили строку нулей
    if find_elem == False:
      r += 1
    #обновляем значение регистра
    self.M[j] = max(self.M[j], r)

  def est_size(self):
    z = 0.0
    for j in range(self.m):
      z += 2 ** (-self.M[j])
    Z = z ** (-1)
    #для подсчета мультипликативного смещения alpha_m использую функцию quad библиотеки scipy
    #функция выдает tuple значение + ошибка, поэтому использую [0] для получения значения
    #в integrand(x) задам интегрируемую функцию
    if self.m < 128:
      def integrand(x):
        return math.log2((2+x)/(1+x)) ** self.m
      alpha_m = (self.m * quad(integrand, 0, float('+inf'))[0]) ** (-1)
    else:
      alpha_m = 0.7213 / (1 + 1.079 / self.m)
    E = alpha_m * self.m ** 2 * Z
    #также в статье упоминается о нескольких корректировках при маленьких/больших значениях
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
