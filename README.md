sexpy — S-expression manipulation toolkit
=========================================

_sexpy_ contains some tools to allow effortless manipulation of data encoded as S-expressions. Its goal is to wrap commonly-used operations into a reusable package, allowing S-expressions to be implemented quickly into any project. Providing comprehensive, powerful set of functionalities is outside the scope of this project.

In particular, _sexpy_ aids in the transformation between these three levels of abstraction:

**<p align='center'>Plain text ⟷ Nested lists ⟷ Python data types</p>**

Example
-------

```python
#
# Example PDDL problem parsing and destructuring
#

import sexpy
import sexpy.schema as sxs

# The source code to parse
src = '''
(define
    (problem BLOCKS-4-1)
    (:domain blocks)
    (:objects A C D B - block)
    (:init 
        (clear B)
        (ontable D) 
        (on B C) 
        (on C A) 
        (on A D) 
        (handempty))
    (:goal (and (on D C) 
                (on C A) 
                (on A B))))
'''

# An schema describing the source layout (using shorthand syntax)
pddl_problem = sxs.desugar(
    sxs.Dict(
        sxs.Ignore('define'),
        ('problem',      sxs.Atom),
        [sxs.Either(
            (':domain',  sxs.Atom),
            (':objects', [sxs.Atom]),
            (':init',    [([sxs.Any])]),
            (':goal',    sxs.Any),
        )]
    )
)

# Parse the source string into nested lists
sexpr = sexpy.loads(src)
print(f'{sexpr = }')

# Validate and destructure the nested lists according to the schema
output = pddl_problem.extract(sexpr[0])
print(f'{output = }')

# Or both at the same time:
output = sexpy.loads(src, schema=pddl_problem)
print(f'{output = }')
```