
class GraphicElement():
	def __init__(self, color, instruction, rotation=None, alpha_channel=1):
		self.color = color
		self.alpha_channel = alpha_channel
		self.instruction = instruction
		self.rotation = rotation