class Element(object):

    def __init__(self, color, gravity, name, temperature, type, durability, dissipation, propagation, transform=None):
        self.color = color
        self.gravity = gravity
        self.name = name
        self.temperature = temperature
        self.type = type
        self.durability = durability
        self.dissipation = dissipation
        self.propagation = propagation
        self.transform = transform

    def copy(self):
        return Element(self.color, self.gravity, self.name, self.temperature, self.type, self.durability, self.dissipation, self.propagation, self.transform)

    def changeElement(self, element, temperature):
        return Element(element.color, element.gravity, element.name, temperature, element.type, element.durability, element.dissipation, element.propagation, element.transform)