# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 15:17:20 2017

@author: Krishna
"""

from pyparsing import *
import re

UPTO, AND, OR, WORDS, CHARACTERS = map(Literal, "UPTO AND OR WORDS CHARACTERS".split())
LBRACE,RBRACE = map(Suppress, "{}")
integer = pyparsing_common.integer()

LINE_CONTAINS, LINE_STARTSWITH, LINE_ENDSWITH = map(Literal,
    """LINE_CONTAINS LINE_STARTSWITH LINE_ENDSWITH""".split()) # put option for LINE_ENDSWITH. Users may use, I don't presently
BEFORE, AFTER, JOIN = map(Literal, "BEFORE AFTER JOIN".split())
keyword = UPTO | WORDS | AND | OR | BEFORE | AFTER | JOIN | LINE_CONTAINS | LINE_STARTSWITH

class Node(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def generate(self):
        pass

class LiteralNode(Node):
    def generate(self):
        return "(%s)" %(''.join(self.tokens[0])) # here, merged the elements, so that re.escape does not have to do an escape for the entire list
    def __repr__(self):
        return repr(self.tokens[0])

class ConsecutivePhrases(Node):
    def generate(self):
        join_these=[]
        tokens = self.tokens[0]
        for t in tokens:  
            tg = t.generate()
            join_these.append(tg)
        return "%s" %(''.join(ele for ele in join_these)) # need to improve on this. Why do I have brackets?. Removed for now
                  
    def __repr__(self):
        return repr(self.tokens[0])

class AndNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        join_these=[]
        for t in tokens[::2]:
            tg = t.generate()
            tg_mod = tg[0]+r'?=.*\b'+tg[1:][:-1]+r'\b)' # to place the regex commands at the right place
            join_these.append(tg_mod)
        joined = ''.join(ele for ele in join_these)
        full = '('+ joined+')'
        return full

    def __repr__(self):
        return ' AND '.join(repr(t) for t in self.tokens[0].asList()[::2])


class OrNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        joined = '|'.join(t.generate() for t in tokens[::2])
        full = '('+ joined+')'
        return full
    def __repr__(self):
        return ' OR '.join(repr(t) for t in self.tokens[0].asList()[::2])

class LineTermNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        ret = ''
        dir_phr_map = {'LINE_CONTAINS': lambda a: 're.search' + a, 'LINE_STARTSWITH': lambda a: 're.search^' + a}
        for line_dir, phr_term in zip(tokens[0::2], tokens[1::2]):
            ret = dir_phr_map[line_dir](phr_term.generate())
        return ret
        
    def __repr__(self):
        tokens = self.tokens[0]
        ret = repr(tokens[0])
        dir_phr_map = {'LINE_CONTAINS': lambda a: a, 'LINE_STARTSWITH': lambda a: '^' + a}
        for line_dir, phr_term in zip(tokens[0::2], tokens[1::2]):
            ret = str(dir_phr_map[line_dir](str(phr_term)))
        return ret
        
class LineAndNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        return '&&'.join(t.generate() for t in tokens[::2])
    def __repr__(self):
        return ' ANDD '.join(repr(t) for t in self.tokens[0].asList()[::2])

class LineOrNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        return '@@'.join(t.generate() for t in tokens[::2])
    def __repr__(self):
        return ' ORR '.join(repr(t) for t in self.tokens[0].asList()[::2])
        
class UpToWordsNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        ret = ''
        word_re = r"([\w]+\s*)"
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            ret += "(%s{0,%d})" % (word_re, op) 
        return ret

    def __repr__(self):
        tokens = self.tokens[0]
        ret = ''
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            ret += " {0-%d WORDS} " % (op) + repr(operand)
        return ret

class UpToCharactersNode(Node):
    def generate(self):
        tokens = self.tokens[0]
        ret = ''
        char_re = r"\w"
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            ret += "((%s){0,%d})" % (word_re, op) 
        return ret

    def __repr__(self):
        tokens = self.tokens[0]
        ret = ''
        for op, operand in zip(tokens[1::2], tokens[2::2]):
            # op contains the parsed "upto" expression
            ret += " {0-%d CHARACTERS} " % (op) + repr(operand)
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
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            ret = operator_opn_map[operator](ret, operand.generate()) # this is basically calling a dict element, and every such element requires 2 variables (a&b), so providing them as ret and op.generate
        return ret
    def __repr__(self):
        tokens = self.tokens[0]
        ret = repr(tokens[0])
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            ret+= ' ' + operator + ' ' + repr(operand)
        return ret

word = ~keyword + Word(alphas, alphanums+'-_')
uptowords_expr = Group(LBRACE + UPTO + integer("numberofwords") + WORDS + RBRACE).setParseAction(UpToWordsNode)
uptochars_expr = Group(LBRACE + UPTO + integer("numberofchars") + CHARACTERS + RBRACE).setParseAction(UpToCharactersNode)
some_words = OneOrMore(word).setParseAction(' '.join, LiteralNode)
phrase_item = some_words | uptowords_expr | uptochars_expr
#phrase_item = Group(OneOrMore(word)).setParseAction((lambda s,l,t: ' '.join(t[0])), LiteralNode) | upto_expr

phrase_expr = infixNotation(phrase_item, 
                            [
                            ((BEFORE | AFTER | JOIN), 2, opAssoc.LEFT, BeforeAfterJoinNode), # was not working earlier, because BEFORE etc. were not keywords, and hence parsed as words
                            (None, 2, opAssoc.LEFT, ConsecutivePhrases),
                            (AND, 2, opAssoc.LEFT, AndNode),
                            (OR, 2, opAssoc.LEFT, OrNode),
                            ],
                            lpar=Suppress('{'), rpar=Suppress('}')
                            ) # structure of a single phrase with its operators
                            
line_term = Group((LINE_CONTAINS|LINE_STARTSWITH)("line_directive") + 
                  (phrase_expr)("phrases")) # basically giving structure to a single sub-rule having line-term and phrase
#                  
line_contents_expr = infixNotation(line_term.setParseAction(LineTermNode),
                                   [(AND, 2, opAssoc.LEFT, LineAndNode),
                                    (OR, 2, opAssoc.LEFT, LineOrNode),
                                    ]
                                   ) # grammar for the entire rule/sentence

tests1 = """LINE_CONTAINS gene {downregulated OR down-regulated OR down regulated} {UPTO 2 WORDS} cells""".splitlines()
tests2 = """LINE_CONTAINS xyz there are {UPTO 3 WORDS} def then {UPTO 4 WORDS} here""".splitlines()
tests3 = """LINE_CONTAINS gene AND other things OR gene mutation""".splitlines()
tests4 = """LINE_CONTAINS gene AND LINE_STARTSWITH Here we OR  LINE_CONTAINS others""".splitlines()
tests5 = """LINE_CONTAINS {overexpress OR overexpressed OR overexpressing} gene here""".splitlines()
tests6 = """LINE_CONTAINS {gene JOIN KO} effect AND LINE_STARTSWITH Here we OR There we""".splitlines()
tests7 = """LINE_CONTAINS the objective of this study was {to identify OR identifying} genes transcriptionally upregulated""".splitlines()

for t in tests7:
    t = t.strip()
    if not t:
        continue
#    print(t, 12)
    print 
    try:
        parsed = line_contents_expr.parseString(t)
    except ParseException as pe:
        print(' '*pe.loc + '^')
        print(pe)
        continue

#print parsed[0],34
print 
#print parsed[0].generate()
temp_regex = parsed[0].generate()
final_regexes1 = re.sub('&&',' AND ',temp_regex) 
final_regexes = re.sub('@@',' OR ',final_regexes1) 
print final_regexes 