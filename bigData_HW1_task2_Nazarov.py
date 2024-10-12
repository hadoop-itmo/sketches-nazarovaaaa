import mmh3 # для вычисления хэша
class BloomFilter():

  def __init__(self, k, n):
    self.filterSize = n
    self.filter = 0
    self.numOfFunc = k

  def put(self, s):
    #устанавливаю бит в определенную позицию для каждой из хэш-функций
    for i in range(self.numOfFunc):
      bitPosition = mmh3.hash(s, i) % self.filterSize
      self.filter |= 1 << bitPosition

  def get(self, s):
    #проверяю значение бита в каждой из позиций, полученных из каждого хэша
    for i in range(self.numOfFunc):
      bitPosition = mmh3.hash(s, i) % self.filterSize
      #если хотя в одном был 0 (то есть фильтр после добавления изменился),
      #сразу возвращаю false
      if (self.filter ^ (self.filter | 1 << bitPosition)) != 0:
        return False
    return True

  def size(self):
    size = 0
    #реализую то же самое, только с делением на число хэш-функций
    while self.filter > 0:
      size += self.filter & 1
      self.filter = self.filter >> 1
    return size / self.numOfFunc