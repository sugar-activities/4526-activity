The question files have a single question per line, and the
question section of the line is separated from the answer section
by a '=' sign.

A '%' sign in the first column of a line indicates that the question is of
the "find the multiples' type.  The number immediately following the
% sign is the base multiplier.  Answers are separated by '~' symbols in
the answer list.

The .dat files each contain 1000 questions.  The file names describe the
contents of the file and adhere to the following format:

<question type>_<max nesting>_<argument range>.dat

The question types were grouped as follows:

multiplication  : only multiplication
division        : only division
addition        : only addition
subtraction     : only subtraction
multdiv         : mixed multiplication and division
addsub          : mixed addition and subtraction
allops          : mixed multiplication, division, addition, and subtraction
multiples       : 'find the multiples' questions
random          : mix of 'find the multiples' questions, and all-ops
                  arithmetic questions

The maximum nesting level refers to the maximum depth of parenthetical
enclosures

p0 = no parenthesis
p1 = at most one level of parenthesis

The argument range gives the minimum and maximum values of the numeric
terms appearing in the questions.  If the minimum value is greater than
or equal to 0, then the answers to the questions are guaranteed 
to be positive



