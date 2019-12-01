from utils import decodeIso6709, currentPosixTime, floatToStr

class IAMAT(object):
  def __init__(self, id, lat, lng, time=None):
    self.id = id
    self.lat = lat
    self.lng = lng
    self.time = time if time != None else currentPosixTime()

  @staticmethod
  def fromParts(parts):
    id = parts[0]
    lat, lng = decodeIso6709(parts[1])
    clientTime = float(parts[2])
    return IAMAT(id, lat, lng, clientTime)
  
  def __str__(self):
    return 'IAMAT ' + self.id + \
      ' ' + floatToStr(self.lat, True) + floatToStr(self.lng, True) + \
      ' ' + floatToStr(self.time) + '\n'

class AT(IAMAT):
  def __init__(self, clientId, lat, lng, clientTime, serverId, serverTime=None, fromId=None):
    super(AT, self).__init__(clientId, lat, lng, clientTime)
    self.serverId = serverId
    self.serverTime = serverTime if serverTime != None else currentPosixTime()
    self.fromId = fromId
  
  @staticmethod
  def fromParts(parts):
    serverId = parts[0]
    timeDiff = float(parts[1])
    clientId = parts[2]
    lat, lng = decodeIso6709(parts[3])
    clientTime = float(parts[4])
    try:
      fromId = parts[5]
    except IndexError:
      fromId = None
    return AT(clientId, lat, lng, clientTime, serverId, clientTime + timeDiff, fromId)
  
  @property
  def timeDiff(self):
    return self.serverTime - self.time
  
  def __str__(self):
    return 'AT ' + self.serverId + ' ' + floatToStr(self.timeDiff) + \
      ' ' + self.id + \
      ' ' + floatToStr(self.lat, True) + floatToStr(self.lng, True) + \
      ' ' + floatToStr(self.time) + \
      ((' ' + self.fromId) if self.fromId != None else '') + '\n'

class WHATSAT(object):
  def __init__(self, id, radius, maxItems):
    self.id = id
    self.radius = radius
    self.maxItems = maxItems

    if radius > 50 or radius < 0:
      raise ValueError('radius is too large')
    if maxItems < 0 or maxItems > 20:
      raise ValueError('maxItems is too large')

  @staticmethod
  def fromParts(parts):
    id = parts[0]
    radius = int(parts[1])
    maxItems = int(parts[2])
    return WHATSAT(id, radius, maxItems)
  
  def __str__(self):
    return 'WHATSAT ' + self.id + \
      ' ' + str(self.radius) + \
      ' ' + str(self.maxItems) + '\n'
      