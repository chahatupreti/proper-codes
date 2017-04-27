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
    def generate(self):
        tokens = self.tokens[0]
#        print (type(tokens[::2]),21)
        join_these=[]
#        print tokens[::2], 26
        for t in tokens[::2]:
            tg = t.generate()
            tg_mod = tg[0]+'?='+tg[1:]
            join_these.append(tg_mod)
        return ''.join(ele for ele in join_these) # change this to the correct form of AND in regex

    def __repr__(self):
        return ' AND '.join(repr(t) for t in self.tokens[0].asList()[::2])


class OrNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        return '|'.join(t.generate() for t in tokens[::2])
    def __repr__(self):
        return ' OR '.join(repr(t) for t in self.tokens[0].asList()[::2])

class LineTermNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        ret = ''
        dir_phr_map = {'LINE_CONTAINS': lambda a: a, 'LINE_STARTSWITH': lambda a: '^' + a}
        for line_dir, phr_term in zip(tokens[0::2], tokens[1::2]):
#            print type(phr_term),37            
            ret = dir_phr_map[line_dir](phr_term.generate())
        return ret
        
    def __repr__(self):
        tokens = self.tokens[0]
        ret = repr(tokens[0])
        dir_phr_map = {'LINE_CONTAINS': lambda a: a, 'LINE_STARTSWITH': lambda a: '^' + a}
        for line_dir, phr_term in zip(tokens[0::2], tokens[1::2]):
            ret = str(dir_phr_map[line_dir](str(phr_term)))
        return ret

class UpToNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        ret = tokens[0].generate()
        print tokens,36,ret
        for t in tokens:
            print t, type(t),39
        word_re = r"\s+\S+"
        space_re = r"\s+"
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            print op,operand,35
            print type(op),36
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
    # This class gets input of the form 'phrase_1 B/A/J phrase_2'. The operator_opn_map is a dict, with the keys
    # being the 3 operators and their enrties being the corresponding action, requiring 2 strings. The for loop
    # finds the operators and their corresponding operands. before that, ret carries the generate() of the 1st
    # element of the input, which would (i believe) invariably be phrase_1. Then, ret calls the dict element corresponding
    # to the operator, and the element takes 2 arguments - one is ret, which is basically generated phrase_1 and 
    # the other is generated current operand, which would basically be phrase_2 and then the dict element (which is
    # basically a lambda function on these 2 arguments), does the relevant operation on these 2 arguments, creates 
    # the corresponding resultant string, and ret now becomes that, and is returned.
    def generate(self):
        tokens = self.tokens[0]
        operator_opn_map = {'BEFORE': lambda a,b: a + '.*?' + b, 'AFTER': lambda a,b: b + '.*?' + a, 'JOIN': lambda a,b: a + '[- ]?' + b}
        ret = tokens[0].generate()
        print (ret, 24)
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            print operator, operand, 26
            ret = operator_opn_map[operator](ret, operand.generate()) # this is basically calling a dict element, and every such element requires 2 variables (a&b), so providing them as ret and op.generate
        print (ret, 25)
        return ret
#        return '|'.join(t.generate() for t in tokens[::2])
    def __repr__(self):
        tokens = self.tokens[0]
        ret = repr(tokens[0])
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            ret+= ' ' + operator + ' ' + repr(operand)
        return ret

phrase_expr = infixNotation(phrase.setParseAction(LiteralNode), 
                            [ 
                            ((BEFORE | AFTER | JOIN), 2, opAssoc.LEFT, BeforeAfterJoinNode), # was not working earlier, because BEFORE etc. were not keywords, and hence parsed as words
                            (upto_expr, 2, opAssoc.LEFT, UpToNode),
                            (AND, 2, opAssoc.LEFT, AndNode),
                            (OR, 2, opAssoc.LEFT, OrNode),
                            ],
                            lpar=Suppress('{'), rpar=Suppress('}')
                            ) # structure of a single phrase with its operators
                            
line_term = Group((LINE_CONTAINS | LINE_STARTSWITH | LINE_ENDSWITH)("line_directive") + 
                  (phrase_expr)("phrases")) # basically giving structure to a single sub-rule having line-term and phrase
                  
line_contents_expr = infixNotation(line_term.setParseAction(LineTermNode),
                                   [(AND, 2, opAssoc.LEFT),
                                    (OR, 2, opAssoc.LEFT),
                                    ]
                                   ) # grammar for the entire rule/sentence
#
#phrase_expr = infixNotation(line_contents_expr,
#        [
#        (upto_expr, 2, opAssoc.LEFT, UpToNode),
#        (AND, 2, opAssoc.LEFT, AndNode),
#        (OR, 2, opAssoc.LEFT, OrNode),
#        ])

tests1 = """LINE_CONTAINS gene {downregulated OR down-regulated OR down regulated} {UPTO 2 WORDS} cells""".splitlines()
tests2 = """LINE_CONTAINS xyz there are {upto 3 words} def then {upto 4 words} here""".splitlines()
tests3 = """LINE_CONTAINS gene AND other things OR gene mutation""".splitlines()
tests4 = """LINE_CONTAINS gene deletion OR gene""".splitlines()

for t in tests2:
    t = t.strip()
    if not t:
        continue
    print(t, 12)
    try:
        parsed = line_contents_expr.parseString(t)
    except ParseException as pe:
        print(' '*pe.loc + '^')
        print(pe)
        continue
#print (parsed[0], 14)
#print (type(parsed[0]))
print parsed[0],34
print 're.search('+parsed[0].generate()+')'