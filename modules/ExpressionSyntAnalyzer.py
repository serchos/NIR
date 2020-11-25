import re

def SyntAnalyzer(expression):
	expression=expression.replace(' ', '')
	expression=expression.replace('	', '')
	return Expression(expression)
		
def Expression(expr):
	bracketNum, symbNum=0, 0

	for symb in expr:
		if symb=='(':
			bracketNum+=1
		elif symb==')':
			bracketNum-=1
		elif (symb=='+' or symb=='-') and bracketNum==0:
			rightTerm=Term(expr[0:symbNum])
			rightExpr=Expression(expr[symbNum+1:])
			
			if rightExpr and rightTerm:
				return True
			else:
				return False
			
		symbNum+=1
	
	return Term(expr)

def Term(term):
	bracketNum, symbNum=0, 0
	
	for symb in term:
		if symb=='(':
			bracketNum+=1
		elif symb==')':
			bracketNum-=1
		elif (symb=='*' or symb=='/') and bracketNum==0:
			rightFactor=Factor(term[0:symbNum])
			rightTerm=Term(term[symbNum+1:])
			if rightFactor and rightTerm:
				return True
			else:
				return False
			break
		
		symbNum+=1

	return Factor(term)
		
	
def Factor(factor):
	if factor[0]=='(' and factor[len(factor)-1]==')':
		return Expression(factor[1:len(factor)-1])
	elif Number(factor):
		return True
	elif Variable(factor):
		return True
	elif Function(factor):
		print(factor)
		return True
	else:
		return False
		
def Number(number):
	if re.fullmatch(r'[-+]?\d+|[-+]?\d+\.\d+', number)!=None:
		return True
	else:
		return False 
		
def Variable(variable):
	if variable=='x' or variable=='X' or variable=='y' or variable=='Y':
		return True
	else:
		return False
		
def Function(function):
	if OneArgFunction(function):
		return Expression(function[function.find('(')+1:len(function)-1])
	elif TwoArgFunction(function):
		arguments=function[function.find('(')+1:len(function)-1]
		bracketNum, symbNum=0, 0
		
		for symb in arguments:
			if symb=='(':
				bracketNum+=1
			elif symb==')':
				bracketNum-=1
			elif symb==',' and bracketNum==0:
				arg1=arguments[:symbNum]
				arg2=arguments[symbNum+1:]
		
				right1Arg=Expression(arg1)
				right2Arg=Expression(arg2)
				
				if right1Arg and right2Arg:
					return True
				else:
					return False
			symbNum+=1
		return False
	else:
		return False

def OneArgFunction(function):
	if re.fullmatch(r'ceil\(.+\)', function) or re.fullmatch(r'fabs\(.+\)', function) or re.fullmatch(r'factorial\(.+\)', function) or re.fullmatch(r'floor\(.+\)', function) or re.fullmatch(r'trunc\(.+\)', function) or re.fullmatch(r'exp\(.+\)', function) or re.fullmatch(r'sqrt\(.+\)', function) or re.fullmatch(r'sin\(.+\)', function) or re.fullmatch(r'cos\(.+\)', function) or re.fullmatch(r'tan\(.+\)', function):
		return True
	else:
		return False

def TwoArgFunction(function):
	if re.fullmatch(r'mod\(.+\)', function) or re.fullmatch(r'div\(.+\)', function) or re.fullmatch(r'pow\(.+\)', function) or re.fullmatch(r'log\(.+\)', function) or re.fullmatch(r'max\(.+\)', function) or re.fullmatch(r'min\(.+\)', function):
		return True
	else:
		return False 

def ChangeFunctionNames(expression):
	expression=expression.replace(' ', '')
	expression=expression.replace('	', '')
	expression=expression.replace('ceil', 'math.ceil')
	expression=expression.replace('fabs', 'math.fabs')
	expression=expression.replace('factorial', 'math.factorial')
	expression=expression.replace('floor', 'math.floor')
	expression=expression.replace('trunc', 'math.trunc')
	expression=expression.replace('exp', 'math.exp')
	expression=expression.replace('sqrt', 'math.sqrt')
	expression=expression.replace('sin', 'math.sin')
	expression=expression.replace('cos', 'math.cos')
	expression=expression.replace('tan', 'math.tan')
	expression=expression.replace('mod', 'math.mod')
	expression=expression.replace('div', 'math.div')
	expression=expression.replace('pow', 'math.pow')
	expression=expression.replace('log', 'math.log')
	expression=expression.replace('max', 'math.max')
	expression=expression.replace('min', 'math.min')	
	return expression