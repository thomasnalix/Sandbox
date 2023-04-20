from Element import Element


class Cell(object):

    def __init__(self, element=Element(), temperature=0):
        self.element = element
        self.temperature = temperature
