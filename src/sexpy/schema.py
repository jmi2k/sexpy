#
# Schema validator loosely inspired by parser combinators
#

class Schema:
	def desugar(self):
		return self

class Passthrough(Schema):
	def __init__(self, schema):
		self.schema = schema

	def desugar(self):
		self.schema = desugar(self.schema)
		return self

	def extract(self, sexpr):
		return self.schema.extract(sexpr)

class Many(Passthrough):
	pass

class Ignore(Passthrough):
	pass

class List(Schema):
	def __init__(self, *args):
		self.schemas = args

	def desugar(self):
		self.schemas = [desugar(schema) for schema in self.schemas]
		return self

	def extract(self, sexpr):
		schemas = self.schemas
		sexpr = sexpr.copy()
		elems = []

		if type(sexpr) is not list:
			raise Exception('invalid type')

		while schemas and sexpr:
			schema = schemas[0]
			sxs, *sexpr = sexpr

			try:
				elem = schema.extract(sxs)
				if type(schema) is not Ignore:
					elems.append(elem)
				if type(schema) is not Many:
					schemas = schemas[1:]
			except Exception as e:
				if type(schema) is Many:
					schemas = schemas[1:]
				else:
					raise e

		if sexpr:
			raise Exception('too many elements in expression')

		return elems

class Dict(List):
	def extract(self, sexpr):
		sexpr = super().extract(sexpr)
		result = {}

		for k, *v in sexpr:
			result[k] = v[0] if len(v) == 1 else v

		return result

class Either(Schema):
	def __init__(self, *args):
		self.alts = args

	def desugar(self):
		self.alts = [desugar(alt) for alt in self.alts]
		return self

	def extract(self, sexpr):
		for alt in self.alts:
			try:
				return alt.extract(sexpr)
			except:
				continue

		raise Exception('expression rejected by schema')

class Literal(Schema):
	def __init__(self, value):
		self.value = value

	def extract(self, sexpr):
		if type(sexpr) not in {str, int, bool}:
			raise Exception('invalid type')
		elif sexpr != self.value:
			raise Exception('expression rejected by schema')

		return sexpr

class Atom(Schema):
	@staticmethod
	def extract(sexpr):
		if type(sexpr) not in {str, int, bool}:
			raise Exception('invalid type')

		return sexpr

class Any(Schema):
	@staticmethod
	def extract(sexpr):
		return sexpr

def desugar(schema):
	if issubclass(type(schema), Schema):
		return schema.desugar()
	elif type(schema) is list:
		return Many(desugar(schema[0]))
	elif type(schema) is tuple:
		desugared = (desugar(elem) for elem in schema)
		return List(*desugared)
	elif type(schema) in {str, int, bool}:
		return Literal(schema)
	else:
		return schema