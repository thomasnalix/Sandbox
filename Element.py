class Element(object):

    def __init__(self, color, gravity, id, name, temperature, type, durability, transform=None):
        self.color = color
        self.gravity = gravity
        self.id = id
        self.name = name
        self.temperature = temperature
        self.type = type
        self.durability = durability
        self.transform = transform

    def copy(self):
        return Element(self.color, self.gravity, self.id, self.name, self.temperature, self.type, self.durability, self.transform)

    def changeElement(self, element, temperature):
        return Element(element.color, element.gravity, element.id, element.name, temperature, element.type, element.durability, element.transform)
