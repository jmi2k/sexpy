#
# Simple S-expression parser
#

DELIMS = {
	'(': ')',
	'[': ']',
	'{': '}',
}

class ParseException(Exception):
	def __init__(self, line, col, message, *args, **kwargs):
		super().__init__(f'{line}:{col}: {message}', *args, **kwargs)
		self.line = line
		self.col = col

def _atom(cur):
	"""Parse atom (literal values)."""
	match = ''

	# Parse whole token
	while cur[0]:
		head, ncur = _fetch(cur)
		if head.isspace() or head in {*DELIMS, *DELIMS.values()}:
			break
		match += head
		cur = ncur

	# If the token is an integer, convert it to a native Python value
	try:
		match = int(match)
	except ValueError:
		pass

	# If the token is a boolean, convert it to a native Python value
	if match == 'True':
		match = True
	elif match == 'False':
		match = False

	return match, cur

def _fetch(cur):
	"""Extract the next character from a cursor and advance its position."""
	src, line, col = cur
	head, *tail = src

	if head == '\n':
		return head, (tail, line+1, 1)
	else:
		return head, (tail, line, col+1)

def _parse(cur, delim):
	"""Parse an S-expression string into a Python nested list structure."""
	sexpr = []
	val = None

	while cur[0]:
		head, ncur = _fetch(cur)

		# Handle character accordingly
		if head.isspace():
			cur = ncur
			continue
		elif head in DELIMS:
			val, ncur = _parse(ncur, DELIMS[head])
		elif head == delim:
			return sexpr, ncur
		elif head in DELIMS.values():
			_, line, col = cur
			raise ParseException(line, col, f"mismatched delimiters (expected '{delim}', got '{head}')")
		else:
			val, ncur = _atom(cur)

		sexpr.append(val)
		cur = ncur

	# This can only be reached when delimiters are balanced.
	# If a delimiter is expected, the expression is malformed.
	if delim:
		_, line, col = cur
		raise ParseException(line, col, f"unexpected EOF (expected '{delim}')")

	return sexpr, cur

def loads(src, schema=None):
	"""Parse an S-expression string into a Python nested list structure."""
	cur = src, 1, 1
	sexpr, _ = _parse(cur, None)
	return sexpr if not schema else schema.extract(sexpr)

def dumps(sexpr):
	"""Turn a nested list structure into its equivalent S-expression string."""
	if type(sexpr) is list:
		inside = ' '.join((dumps(elem) for elem in sexpr))
		return f'({inside})'
	elif type(sexpr) is str:
		return sexpr
	elif type(sexpr) in {int, bool}:
		return str(sexpr)