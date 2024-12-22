import mmh3 # для вычисления хэша
class BloomFilter():

  def __init__(self, n):
    self.filterSize = n
    self.filter = 0

  def put(self, s):
    #определение позиции
    bitPosition = mmh3.hash(s) % self.filterSize
    #обновление фильтра
    self.filter |= 1 << bitPosition

  def get(self, s):
    #определение позиции
    bitPosition = mmh3.hash(s) % self.filterSize
    #изменится ли фильтр после добавления 
    if (self.filter ^ (self.filter | 1 << bitPosition)) == 0:
      return True
    else:
      return False

  def size(self):
    size = 0
    #сдигаю по одному биту и подсчитываю число единиц
    while self.filter > 0:
      size += self.filter & 1
      self.filter = self.filter >> 1
    return size