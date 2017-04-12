import hou, re

def printColor():
	try:
		node = hou.selectedNodes()[0]
		print node.color()
	except(IndexError):
		pass
		

printColor()