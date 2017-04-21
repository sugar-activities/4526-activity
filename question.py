#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Kuku Anakula
# Copyright (C) 2007, Julius B. Lucks, Adrian DelMaestro, Sera L. Young
# Copyright (C) 2012, Alan Aguiar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Julius B. Lucks <julius@younglucks.com>
# Alan Aguiar <alanjas@gmail.com>

import random
import math
import re

EQ_TYPE        = 0
MULTIPLES_TYPE = 1
ADD_TYPE       = 2
SUB_TYPE       = 3
ADDSUB_TYPE    = 4
MULT_TYPE      = 5
DIV_TYPE       = 6
MULTDIV_TYPE   = 7
N_TYPE         = 8

#**********************************
#**********************************
class ParseError (Exception) :
    pass

class OptionError (Exception):
    pass

class FileError (Exception):
    pass

#**********************************
#**********************************
class QuestionMaker (object) :
    def __init__ (self,newseed) :
        self.nop       = 4
        self.addsub    = 2
        self.operators = ("+","-","x","/")
        random.seed(newseed)
    #********

    def Gen_arg (self,num_range, pcut, curr_level, max_level, opindex, oplist) :
        #Generates equation terms
        #SHOULD only be called by Make_eq_question

        #TAKES the range of allowed numbers
        #TAKES the probability of generating a nested statement
        #TAKES the current nesting level
        #TAKES the maximum nesting level
        #TAKES an integer giving the index of the last operator used in the question
        #TAKES list of available operators

        #RETURNS a tuple with [0] = a string containing the term and [1] = the integer value of the term

        rval = random.uniform(0,1)
        if ( (rval <= pcut) and (opindex >= self.addsub) and (curr_level <= max_level) ) :
            if (curr_level == max_level) :
              new_op_list = ["+","-","+","-"] #redirect the reference
            else :
              new_op_list = oplist
            #endif

            (arg,ans) = self.Make_eq_question(num_range, pcut, (curr_level + 1),max_level,new_op_list)
            arg = "(" + arg + ")"
        else :
            arg = round(random.uniform(num_range[0],num_range[1]))
            ans = int(arg)
            arg = str(ans)
        #endif
        return(arg,ans)
    #********

    def Make_eq_question (self,num_range, pcut, curr_level, max_level, op_list):
        #Generates a question string, along with an integer answer

        #TAKES the range numbers allowed in the question
        #if the minimum of the range is >0 the answer will also be > 0
        #TAKES the probability of generating a nested term
        #TAKES an integer >= 1 which gives the current level of nesting
        #TAKES an integer >= 0 which gives the maximum nesting level
        #TAKES an list of characters representing the allow operators

        #RETURNS a tuple with a question string and an integer answer

        nflag = True
        while ( nflag == True ) :
            qstring = ""
            opindex = int(math.floor(random.uniform(0,self.nop)))
            op      = op_list[opindex]

            #ensure an integer answer whenever a div op is selected
            if (op == "/") :
                ans2 = 0
                while (ans2 == 0) :
                    (arg2,ans2) = self.Gen_arg (num_range, pcut, curr_level, max_level, opindex,op_list)
                #end while
                ans1 = int(round(random.uniform(num_range[0],num_range[1]))*ans2)
                arg1 = str(ans1)
            else :
                (arg1,ans1) = self.Gen_arg (num_range, pcut, curr_level, max_level, opindex,op_list)
                (arg2,ans2) = self.Gen_arg (num_range, pcut, curr_level, max_level, opindex,op_list)
            #endif

            qstring = arg1 + " " + op + " " + arg2
        
            if (op == "+") :
                ans = ans1 + ans2
            elif (op == "-") :
                ans = ans1 - ans2
            elif (op == "x") :
                ans = ans1 * ans2
            else :
                ans = ans1 / ans2
            #endif

            if ( (ans > 0) or (num_range[0] < 0) ):
                nflag = False
            #end if
        #end while
        
        return (qstring,ans)
    #end Make_eq_question
    #********

    def Make_multiples_question (self,num_range,max_ans) :
        #Makes a 'find the multiples' type question

        #TAKES a upper bound on the multiplier (ie: find the multiples of something in |[2,num_range]|)
        #TAKES a an integer giving the maximum number of answers (# of answers in [1,max_ans])

        #RETURNS a string with the question in the format "%n" where n is the base multiplier,
        #and an list of answers delimited by sim signs

        ans_string = ""
        n_ans      = int(round(random.uniform(1,max_ans)))
        base_val   = int(round(random.uniform(2,num_range[1])))

        ans_list=[]
        ans = base_val*int(round(random.uniform(0,num_range[1])))
        ans_list.append(ans)
        for i in range(2,n_ans) :
            ans = base_val*int(round(random.uniform(0,num_range[1])))
            ans_list.append(ans)
        #end for
        if (num_range[0] < 0):
            base_val = base_val*((-1) **int(math.floor(random.uniform(0,10))) )
            for i in range(0,len(ans_list)) :
                ans_list[i] = ans_list[i] * ((-1) **int(math.floor(random.uniform(0,10))) )
        #end if

        ans_string = str(ans_list[0])
        for i in range(1,len(ans_list)-1):
            ans_string += "~" + str(ans_list[i])
        #end for

        qstring = "%" + str(base_val)

        return(qstring,ans_string)
    #end Make_mult_question
    #**********

    def Make_random_question(self,bias,num_range,parameters) :
        #Makes a question of a random type

        #TAKES the cut off for deciding between a standard question and a multiples type question
        #TAKES the allowed range of the question arguments
        #TAKES a list of parameters [0] = max answers in a 'multiples' type question
        #[1] = pcut for a standard equation question, [2] = max_level for a standard equation question

        rval = random.uniform(0,1)
        eq_params   = [parameters[1],parameters[2]]
        mult_params = [parameters[0]]
        if (rval > bias) :
            q = self.Make_question(EQ_TYPE,num_range,eq_params)
        else :
            q = self.Make_question(MULTIPLES_TYPE,num_range,mult_params)
        #endif

        return(q)

    
    def Make_question (self, type_flag, num_range, parameters) :
        #Makes a question of a specific type

        #TAKES an integer that determines the question type
        #TAKES the allowable range for numbers in the question
        #TAKES an array of question type-specific paramters
        # if type = standard equation,
        #   parameters[0] = a float in [0,1] that gives the probability of generating a nested statement
        #   parameters[1] = maximum nesting level
        # if type_flag = find the multiples question
        #   parameters[0] = maximum number of multiples in the answer set

        #RETURNS a question object

        qstring     = ""
        #no switch-like statement unfortunately
        if (type_flag == EQ_TYPE) : #a standard equation type question
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = parameters[0]
            max_level   = parameters[1]
            currlevel   = 1
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,self.operators)
            a = str(int(a))
        elif (type_flag == MULTIPLES_TYPE) : #a 'find the multiples' type question
            if (len(parameters) != 1) :
                raise(OptionError)
            #endif
            max_ans = parameters[0]
            (qstring,a) = self.Make_multiples_question(num_range,max_ans)
        elif (type_flag == ADD_TYPE) :
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = 0
            max_level   = 0
            currlevel   = 1
            oplist      = ["+","+","+","+"]
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,oplist)
            a = str(int(a))
        elif (type_flag == SUB_TYPE) :
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = 0
            max_level   = 0
            currlevel   = 1
            oplist      = ["-","-","-","-"]
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,oplist)
            a = str(int(a))
        elif (type_flag == ADDSUB_TYPE) :
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = 0
            max_level   = 0
            currlevel   = 1
            oplist      = ["+","-","+","-"]
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,oplist)
            a = str(int(a))
        elif (type_flag == MULT_TYPE) :
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = 0
            max_level   = 0
            currlevel   = 1
            oplist      = ["x","x","x","x"]
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,oplist)
            a = str(int(a))
        elif (type_flag == DIV_TYPE) :
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = 0
            max_level   = 0
            currlevel   = 1
            oplist      = ["/","/","/","/"]
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,oplist)
            a = str(int(a))
        elif (type_flag == MULTDIV_TYPE) :
            if (len(parameters) != 2) :
                raise(OptionError)
            #endif
            pcut        = 0
            max_level   = 0
            currlevel   = 1
            oplist      = ["x","/","x","/"]
            (qstring,a) = self.Make_eq_question(num_range,pcut,currlevel,max_level,oplist)
            a = str(int(a))
        else :
            raise (OptionError)

        new_q = Question(qstring,a)

        return(new_q)
    #end Make_Question
#**********************************
#**********************************
class QuestionFileIO (object) :
    def __init__ (self) :
        pass
#       self.file_name = file_name
#       self.Read_questions()
    #********

    def Read_questions (self,file_name) :
        #Reads questions from a file

        #TAKES a file_name

        #RETURNS a list of Question objects
        try:
            f = file(file_name,"r")
        except IOError:
            raise(FileError)
        
        question_list = []
        for line in f.readlines():
            if not re.match('#',line):
                (q,a) = line[:-1].split("=")  #chomp
                question_list.append(Question(q,a))
            
            # a = re.sub('\s+','',a)

        if (len(question_list) < 1) :
            raise ParseError

        return (QuestionList(question_list))
    #end Read_questions
    #********

    def Write_questions (self,file_name,question_list) :
        #Writes questions to a file

        #TAKES a file anme
        #TAKES a list of Question objects

        #RETURNS null

        try:
            f = file(file_name,"w+")
        except IOError:
            raise(FileError)

        for i in question_list :
            f.write(i.q_string_raw+" = "+i.a_string_raw+"\n")

        f.close()
    #end Write_questions
    #********
    
#**********************************
#**********************************
class Question (object) :
    def __init__ (self, q_raw, a_raw) :
        self.q_string_raw     = q_raw
        self.a_string_raw     = a_raw

        (self.type,self.q_string,self.a_list) = self.Parse_question(q_raw,a_raw)
        self.n_answers        = len(self.a_list)
    #**********

    def Parse_question(self,q_string,a_string) :
        #Parses question and answer strings

        #TAKES a unmodified question string
        #TAKES an unmodified answer string

        #RETURNS an int representing the question type, a formatted question string,
        #and a *list* of integers representing the answer(s) to the question
        
        # a multiples question
        if (q_string[0] == "%") :
            try :
                a_list     = map(int,a_string.split("~"))
                qparts     = q_string.split("%")
            except TypeError() :
                raise ParseError
            
            type       = MULTIPLES_TYPE
            # new_string = "Find the multiples of " + str(qparts[1])
            #Modify for smaller string
            new_string = "Divis by " + str(qparts[1])
        elif re.search('\.jpg',a_string): #numbers/01x.jpg
            type       = N_TYPE
            new_string = q_string
            a_list     = [re.sub('\s+','',a_string)] #remove white space
        else :
            try :
                a_list = [int(a_string)]
            except ValueError() :
                raise ParseError

            type       = EQ_TYPE
            new_string = q_string
        #end if

        return(type,new_string,a_list)
    #end Parse_question
    #********

#**********************************
#**********************************    

class QuestionList(object):
    """Manages what the next question is."""
    
    def __init__(self,question_list):
        self.question_list = question_list
        self.num_questions = len(question_list)
        self.ind = 0
    
    def next(self):
        """returns next question"""
        #might want to use a generator here?
        
        #loop back questions
        if self.ind == self.num_questions:
            self.ind = 0
        
        self.ind += 1
        return self.question_list[self.ind-1]
    
    def get_all_answers(self):
        """docstring for get_all_answers"""
        # return [q.a_string for q in self.question_list]
        a_list = []
        for q in self.question_list:
            a_list.extend(q.a_list)
        return a_list


class QuestionGroup(object):
    """Manages several QuestionList's
    
    Returns the QuestionList that is next in the
    series.
    """
    def __init__(self, question_lists):
        self.question_lists = question_lists
        self.length_lists = [len(l.get_all_answers()) 
                             for l in self.question_lists]
        #1st index for question_listt
        #2nd for question within a question_list
        self.ind = [0,0]
    
    def next(self):
        """return question list corresponding to next question"""
        if self.ind[1] == self.length_lists[self.ind[0]]:
            self.ind[0] += 1
            self.ind[1]  = 0
        if self.ind[0] == len(self.question_lists):
            self.ind = [0,0]
        self.ind[1] += 1
        # print 'ind', self.ind
        return self.question_lists[self.ind[0]]
        



def main () :
    qfr   = QuestionFileIO()
    qlist = qfr.Read_questions("allops_p1_0-10.dat")

    nq = len(qlist)
    print ("%d" % (nq)) 

    for i in range(0,nq) :
       print ("%s : %s |%s = %s|" % (i,qlist[i].type,qlist[i].q_string,qlist[i].a_list))
#      print ("%s" % (qlist[i].q_string))
    #end for

#    qm   = QuestionMaker(348)
#    qfr  = QuestionFileIO()

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_random_question(0.0,[-10,10],[5,0.9,3]))
#    #endfor
#    qfr.Write_questions("test.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULT_TYPE,[0,10],[0,0]))
#    #end for
#    qfr.Write_questions("multiplication_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULT_TYPE,[0,100],[0,0]))
#    #end for
#    qfr.Write_questions("multiplication_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULT_TYPE,[-10,10],[0,0]))
#    #end for
#    qfr.Write_questions("multiplication_p0_-10-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULT_TYPE,[-100,100],[0,0]))
#    #end for
#    qfr.Write_questions("multiplication_p0_-100-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(DIV_TYPE,[0,10],[0,0]))
#    #end for
#    qfr.Write_questions("division_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(DIV_TYPE,[0,100],[0,0]))
#    #end for
#    qfr.Write_questions("division_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(DIV_TYPE,[-10,10],[0,0]))
#    #end for
#    qfr.Write_questions("division_p0_-10-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(DIV_TYPE,[-100,100],[0,0]))
#    #end for
#    qfr.Write_questions("division_p0_-100-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(ADD_TYPE,[0,10],[0,0]))
#    #end for
#    qfr.Write_questions("addition_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(ADD_TYPE,[0,100],[0,0]))
#    #end for
#    qfr.Write_questions("addition_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        new_q = qm.Make_question(SUB_TYPE,[0,10],[0,0])
#        qlist.append(new_q)
#    #end for
#    qfr.Write_questions("subtraction_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        new_q = qm.Make_question(SUB_TYPE,[0,100],[0,0])
#        qlist.append(new_q)
#    #end for
#    qfr.Write_questions("subtraction_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        new_q = qm.Make_question(ADDSUB_TYPE,[0,10],[0,0])
#        qlist.append(new_q)
#    #end for
#    qfr.Write_questions("addsub_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        new_q = qm.Make_question(ADDSUB_TYPE,[0,100],[0,0])
#        qlist.append(new_q)
#    #end for
#    qfr.Write_questions("addsub_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        new_q = qm.Make_question(ADDSUB_TYPE,[-10,10],[0,0])
#        qlist.append(new_q)
#    #end for
#    qfr.Write_questions("addsub_p0_-10-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        new_q = qm.Make_question(ADDSUB_TYPE,[-1000,100],[0,0])
#        qlist.append(new_q)
#    #end for
#    qfr.Write_questions("addsub_p0_-100-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULTDIV_TYPE,[0,10],[0,0]))
#    #end for
#    qfr.Write_questions("multdiv_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULTDIV_TYPE,[0,100],[0,0]))
#    #end for
#    qfr.Write_questions("multdiv_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULTDIV_TYPE,[-10,10],[0,0]))
#    #end for
#    qfr.Write_questions("multdiv_p0_-10-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULTDIV_TYPE,[-100,100],[0,0]))
#    #end for
#    qfr.Write_questions("multdiv_p0_-100-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(EQ_TYPE,[0,10],[0.5,0]))
#    #end for
#    qfr.Write_questions("allops_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(EQ_TYPE,[0,100],[0.5,0]))
#    #end for
#    qfr.Write_questions("allops_p0_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(EQ_TYPE,[0,10],[0.5,1]))
#    #end for
#    qfr.Write_questions("allops_p1_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(EQ_TYPE,[0,100],[0.5,1]))
#    #end for
#    qfr.Write_questions("allops_p1_0-100.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULTIPLES_TYPE,[0,10],[5]))
#    #end for
#    qfr.Write_questions("multiples_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_question(MULTIPLES_TYPE,[-10,10],[5]))
#    #end for
#    qfr.Write_questions("multiples_p0_-10-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_random_question(0.2,[0,10],[5,0.3,0]))
#    #endfor
#    qfr.Write_questions("random_p0_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_random_question(0.2,[-10,10],[5,0.3,0]))
#    #endfor
#    qfr.Write_questions("random_p0_-10-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_random_question(0.2,[0,10],[5,0.3,1]))
#    #endfor
#    qfr.Write_questions("random_p1_0-10.dat",qlist)

#    qlist=[]
#    for i in range(0,1000) :
#        qlist.append(qm.Make_random_question(0.2,[-10,10],[5,0.3,1]))
#    #endfor
#    qfr.Write_questions("random_p1_-10-10.dat",qlist)

if (__name__ == "__main__") :
    main()
