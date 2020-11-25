import os, io, math

def MetricL1(str, NewDataNormal, Weight=[]):
	dist=0
 
	if Weight:
		for i, j, w in zip(str, NewDataNormal, Weight):
			if isinstance(i, list)==True:
				dist+=MetricL1(i, j, [w for ii in i])
			else:
				dist+=math.fabs((i-j)*w)
	else:
		for i, j in zip(str, NewDataNormal):
			if isinstance(i, list)==True:
				dist+=MetricL1(i, j)
			else:
				dist+=math.fabs(i-j)	

	return dist

def MetricEuclid(str, NewDataNormal, Weight=[]):
	dist=0
 
	if Weight:
		for i, j, w in zip(str, NewDataNormal, Weight):
			if isinstance(i, list)==True:
				dist+=math.pow(w*MetricL1(i, j, [w for ii in i]), 2)
			else:
				dist+=math.pow(w*(i-j), 2)
	else:
		for i, j in zip(str, NewDataNormal):
			if isinstance(i, list)==True:
				dist+=math.pow(MetricL1(i, j), 2)
			else:
				dist+=math.pow(i-j, 2)		

	return math.sqrt(dist)
 
def MetricChebyshev(str, NewDataNormal, Weight=[]):
	dist=0

	if Weight:	
		for i, j, w in zip(str, NewDataNormal, Weight):
			if isinstance(i, list)==True:
				buf=MetricChebyshev(i, j, [w for ii in i])
			else:
				buf=math.fabs(w*(i-j))
			if buf>dist:
				dist=buf
	else:
		for i, j in zip(str, NewDataNormal):
			if isinstance(i, list)==True:
				buf=MetricChebyshev(i, j)
			else:
				buf=math.fabs(i-j)
			if buf>dist:
				dist=buf

	return dist

def MetricSquareEuclid(str, NewDataNormal, Weight=[]):
	dist = 0

	if Weight:
		for i, j, w in zip(str, NewDataNormal, Weight):
			if isinstance(i, list) == True:
				dist += math.pow(w*MetricL1(i, j, [w for ii in i]), 2)
			else:
				dist += math.pow(w*(i - j), 2)
	else:
		for i, j in zip(str, NewDataNormal):
			if isinstance(i, list) == True:
				dist += math.pow(MetricL1(i, j), 2)
			else:
				dist += math.pow(i - j, 2)				
				
	return dist

def MetricMinkowskiWithPow5(str, NewDataNormal, Weight=[]):
	dist = 0

	if Weight:
		for i, j, w in zip(str, NewDataNormal, Weight):
			if isinstance(i, list) == True:
				dist += math.pow(w*MetricL1(i, j, [w for ii in i]), 5)
			else:
				dist += math.pow(w*(i - j), 5)
	else:
		for i, j in zip(str, NewDataNormal):
			if isinstance(i, list) == True:
				dist += math.pow(MetricL1(i, j), 5)
			else:
				dist += math.pow(i - j, 5)
	
	return math.pow(dist, 1//5)
 
def MetricUser(str, NewDataNormal, Weight, MetricStr):
 dist=0

 for x, y, w in zip(str, NewDataNormal, Weight):
  if isinstance(x, list)==True:
   buf=MetricUser(x, y, [w for xx in x], MetricStr)
  else:
   dist+=eval(MetricStr)

 return dist