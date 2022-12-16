bison -d -o parserOut.cpp parser.y

flex -o lexerOut.c lexer.l

g++ -o kompilator parserOut.cpp lexerOut.c

del lexerOut.c parserOut.cpp parserOut.hpp