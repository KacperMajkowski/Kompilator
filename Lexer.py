from sly import Lexer


class CompLexer(Lexer):
    tokens = {"A", "B", "C"}
    
    A = r'ab'
    B = r'cba'
    C = r'c'
    
    
if __name__ == '__main__':
    data = 'abcbac'
    lexer = CompLexer()
    for tok in lexer.tokenize(data):
        print('type=%r, value=%r' % (tok.type, tok.value))