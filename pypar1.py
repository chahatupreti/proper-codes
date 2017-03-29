# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 11:24:06 2017

@author: Krishna
"""

from pyparsing import *
import re

UPTO, AND, OR, WORDS = map(Literal, "upto AND OR words".split())
LBRACE,RBRACE = map(Suppress, "{}")
integer = pyparsing_common.integer()

LINE_CONTAINS, LINE_STARTSWITH, LINE_ENDSWITH = map(Literal,
    """LINE_CONTAINS LINE_STARTSWITH LINE_ENDSWITH""".split()) # put option for LINE_ENDSWITH. Users may use, I don't presently
BEFORE, AFTER, JOIN = map(Literal, "BEFORE AFTER JOIN".split())
keyword = UPTO | WORDS | AND | OR | BEFORE | AFTER | JOIN
word = ~keyword + Word(alphas)
phrase = Group(OneOrMore(word)).setParseAction(traceParseAction(lambda s,l,t: ' '.join(t[0])))
upto_expr = Group(LBRACE + UPTO + integer("numberofwords") + WORDS + RBRACE)

class Node(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def generate(self):
        pass

class LiteralNode(Node):
    def generate(self):
#        print (self.tokens[0], 20)
#        for el in self.tokens[0]:
#            print (el,type(el), 19)
#        print (type(self.tokens[0]), 18)
        return "(%s)" %(' '.join(self.tokens[0])) # here, merged the elements, so that re.escape does not have to do an escape for the entire list
    def __repr__(self):
        return repr(self.tokens[0])

class AndNode(Node):
    print 224
    def generate(self):
        tokens = self.tokens[0]
        print (type(tokens[::2]),21)
        return '.*'.join(t.generate() for t in tokens[::2]) # change this to the correct form of AND in regex

    def __repr__(self):
        return ' AND '.join(repr(t) for t in self.tokens[0].asList()[::2])


class OrNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        return '|'.join(t.generate() for t in tokens[::2])
    def __repr__(self):
        return ' OR '.join(repr(t) for t in self.tokens[0].asList()[::2])


class UpToNode(Node):
    print 224
    def generate(self):
        tokens = self.tokens[0]
        ret = tokens[0].generate()
        print (123123)
        word_re = r"\s+\S+"
        space_re = r"\s+"
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            ret += "((%s){0,%d}%s)" % (word_re, op.numberofwords, space_re) + operand.generate()
        print ret
        return ret

    def __repr__(self):
        tokens = self.tokens[0]
        ret = repr(tokens[0])
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            ret += " {0-%d WORDS} " % (op.numberofwords) + repr(operand)
        return ret

class BeforeAfterJoinNode(Node):
    print 223
    def generate(self):
        print 23
        tokens = self.tokens[0]
        operator_opn_map = {'BEFORE': lambda a,b: a + '.*?' + b, 'AFTER': lambda a,b: b + '.*?' + a, 'JOIN': lambda a,b: a + '[- ]?' + b}
        ret = tokens[0].generate()
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            ret = operator_opn_map[operator](ret, operand.generate())
        return ret
#        return '|'.join(t.generate() for t in tokens[::2])
    def __repr__(self):
        return ' MMOR '.join(repr(t) for t in self.tokens[0].asList()[::2])

phrase_expr = infixNotation(phrase.setParseAction(LiteralNode), 
                            [ 
                            ((BEFORE | AFTER | JOIN), 2, opAssoc.LEFT, BeforeAfterJoinNode), # was not working earlier, because BEFORE etc. were not keyowrds, and hence parsed as words
                            (upto_expr, 2, opAssoc.LEFT, UpToNode),
                            (AND, 2, opAssoc.LEFT, AndNode),
                            (OR, 2, opAssoc.LEFT, OrNode),
                            ]) # structure of a single phrase with its operators
#line_term = Group((LINE_CONTAINS | LINE_STARTSWITH | LINE_ENDSWITH)("line_directive") + 
#                  Group(phrase_expr)("phrases")) # basically giving structure to a single sub-rule having line-term and phrase
#line_contents_expr = infixNotation(line_term,
#                                   [(AND, 2, opAssoc.LEFT,),
#                                    (OR, 2, opAssoc.LEFT),
#                                    ]
#                                   ) # grammar for the entire rule/sentence
#
#phrase_expr = infixNotation(line_contents_expr,
#        [
#        (upto_expr, 2, opAssoc.LEFT, UpToNode),
#        (AND, 2, opAssoc.LEFT, AndNode),
#        (OR, 2, opAssoc.LEFT, OrNode),
#        ])

tests1 = """overexpressing gene JOIN other things""".splitlines()
tests2 = """xyz there are {upto 3 words} def then {upto 4 words} here""".splitlines()
for t in tests1:
    t = t.strip()
    if not t:
        continue
    print(t, 12)
    try:
        parsed = phrase_expr.parseString(t)
    except ParseException as pe:
        print(' '*pe.loc + '^')
        print(pe)
        continue
#print (parsed[0], 14)
#print (type(parsed[0]))
print parsed[0]
print(parsed[0].generate(), 15)
