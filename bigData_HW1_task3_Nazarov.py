import mmh3 # для вычисления хэша
class CountingBloomFilter:

  def __init__(self, k, n, cap):
    self.filterSize = n
    self.filter = 0
    self.cap = cap
    self.numOfFunc = k
    #единичный фильтр
    self.filledFilter = 0
    for j in range(cap):
      self.filledFilter |= 1 << j

  def put(self, s):
    for i in range(self.numOfFunc):
      counterNumber = mmh3.hash(s, i) % self.filterSize
      #сдвигаем вправо, чтобы наш счетчик оказался самой младшей частью битовой строки
      tempCounter = self.filter >> (counterNumber * self.cap)
      #обрезаю фильтр слева и выделяю сам счетчик
      tempCounter &= self.filledFilter
      #проверяем, что счетчик не переполнился
      if ((tempCounter+1) >> self.cap) == 0:
        tempCounter += 1
        #сбрасываем текущее значение за счет битового "И"
        #использую доп. переменную, в которой буду хранить фильтр единиц с обнулением в указанном счетчике
        emptyCounterFilter = 0
        for i in range(self.filterSize):
          if i == counterNumber:
            for j in range(self.cap):
              emptyCounterFilter |= 0 << (i * self.cap + j)
          else:
            for j in range(self.cap):
              emptyCounterFilter |= 1 << (i * self.cap + j)
        #устанавливаем новое значение счетчика за счет "ИЛИ"
        self.filter &= emptyCounterFilter
        self.filter |= tempCounter << (counterNumber * self.cap)

  def get(self, s, teta):
    for i in range(self.numOfFunc):
      counterNumber = mmh3.hash(s, i) % self.filterSize
      #выделяем счетчик аналогично put
      tempCounter = self.filter >> (counterNumber * self.cap)
      tempCounter &= self.filledFilter
      #если значение меньше порога, то сразу возвращаем False
      if tempCounter < teta:
        return False
    #если все счетчики не меньше порога, возвращаем True
    return True

  def size(self):
    size = 0
    for i in range(self.filterSize):
      #выделяем счетчик аналогично put
      tempCounter = self.filter >> (i * self.cap)
      tempCounter &= self.filledFilter
      #в size ведем подсчет суммы счетчиков
      size += tempCounter
    return size / self.numOfFunc