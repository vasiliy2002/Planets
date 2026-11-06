from graphic_element import GraphicElement
from kivy.graphics import Color, Ellipse, Line, Rectangle, PushMatrix, PopMatrix, Rotate
from body_graphic import BodyGraphic

class GraphicManager():
    def __init__(self):
        self.background = None
        self.bodies_graphic = list()

    def get_body_by_name(self, name):
        for body_graphic in self.bodies_graphic:
            if body_graphic.name == name:
                return body_graphic
        return None

    def create_background(self, canvas, cx, cy, w, h, rgba):
        with canvas:
            color = Color(*rgba)
            instruction = Rectangle(pos=(cx, cy), size=(w, h))

        self.background = GraphicElement(color, instruction)

    def create_body(self, canvas, name, body_color, body_size, orbit_color=None, orbit_size=None, 
        line_color=None, rotation_angle=None, rotation_center=None):
        with canvas.before:

            rotation = None
            if rotation_angle is not None:
                PushMatrix()
                rotation = Rotate(angle=rotation_angle, axis=(0, 0, 1), origin=rotation_center)

            orbit_color_graphics, orbit_instruction, orbit_element = None, None, None
            if orbit_color:
                orbit_color_graphics = Color(*orbit_color)
                orbit_instruction = Line(ellipse=orbit_size, width=1)
                orbit_element = GraphicElement(orbit_color_graphics, orbit_instruction, rotation, orbit_color[-1])

            if rotation_angle is not None:
                PopMatrix()

            line_color_graphics, line_instruction, line_element = None, None, None
            if line_color:
                line_color_graphics = Color(*line_color)
                line_instruction = Line(width=1)
                line_element = GraphicElement(line_color_graphics, line_instruction)

        with canvas:
            circle_color = Color(*body_color)
            circle_instruction = Ellipse(size=(body_size, body_size))
            body_element = GraphicElement(circle_color, circle_instruction)

        body = BodyGraphic(name, body_element, orbit_element, line_element)
        self.bodies_graphic.append(body)
        return body

