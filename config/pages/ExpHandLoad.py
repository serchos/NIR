import io, math, random, re, os

from flask import Blueprint, render_template, request, session, url_for, redirect, escape, current_app
from config.db import get_db
from owlready2 import *

from modules.OntologyMethods import createHierarchyTreeDict, getNodeKidsList, get_graph_hierarchy, getEdges
bp = Blueprint('ExpHandLoad', __name__, url_prefix='/ExpHandLoad')

@bp.route('/', methods=('GET', 'POST'))
def ExpHandLoad():
	db = get_db()
	mistake_message = ''
	if 'create_ontology_mistake' in session:
		mistake_message = escape(session['create_ontology_mistake']).capitalize()
		session.pop('create_ontology_mistake', None)
	return render_template('ExpHandLoad.html', mistake_message = mistake_message)
	
@bp.route('/InputBP',  methods = ['GET', 'POST'])
def AcceptAndCreateScheme(): # создание таблицы в бп
 ColCount=int(request.form['ColCount'], 10) # преобразовать в int в десятичной системе
 global BPName, TabInfo, TabData
 global DescriptionBPName, DescriptionTabInfo, TabDescrData
 BPName=request.form['BPName']
 OntologyBPName = BPName + 'Ontology.owl'
 DescriptionBPName = BPName + 'Description'
 StrNames = ''
 StrDescNames = ''
 StrParamNames = ''
 StrDescriptions = ''
 StrTypes = ''
 StrRangeFrom = ''
 StrRangeTo = ''
 StrWeights = ''
 StrUnits = ''
 TextFile = ''
 Description_Str_Names = ''
 conn = get_db()
 cur = conn.cursor()
 for i in range(0,ColCount):
  StrNames = StrNames+', '+request.form['ColName'+str(i)]+' '+request.form['ColType'+str(i)] # str - переводит строку в id
 StrNames = StrNames + ', sampleCode VARCHAR(10), qualityCode VARCHAR(10)'
 Description_Str_Names = ', '+ 'Параметр' + ' ' + 'text' + ', ' + 'Описание' + ' ' + 'text' + ', '+ 'Тип' + ' ' + 'text' + ', ' + 'Единицы_измерения' + ' ' + 'text' + ', ' + 'Диапазон_от' + ' ' + 'real' + ', ' + 'Диапазон_до' + ' ' + 'real' + ', ' + 'Вес' + ' ' + 'real'
 for i in range(0,ColCount-1):
  StrParamNames = StrParamNames + ', ' + request.form['ColName' + str(i)]
  StrDescriptions = StrDescriptions + ', ' + request.form['DescriptionName'+str(i)]
  StrTypes = StrTypes + ', ' + request.form['ColType' + str(i)]
  StrUnits = StrUnits + ', ' + request.form['ColUnit' + str(i)] #todo
  StrRangeFrom = StrRangeFrom + ', ' + request.form['RangeFrom' + str(i)]
  StrRangeTo = StrRangeTo + ', ' + request.form['RangeTo' + str(i)]
  StrWeights = StrWeights + ', ' + request.form['ColWeights' + str(i)]
 StrDescNames = 'Параметр' + ', ' + 'Описание' + ', ' + 'Тип' + ', ' + 'Единицы_измерения' + ', ' + 'Диапазон_от' + ', ' + 'Диапазон_до' + ', ' + 'Вес'
 
 ontology_file = request.files['OntologyFile']
 if ontology_file.filename != '':
  ontology_file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], OntologyBPName))
  
  old_path = "file://" + os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], OntologyBPName)
  ontology_path = old_path.replace(os.sep, '/')
  world2 = World()
  onto = world2.get_ontology(ontology_path).load()
  situation_params = getNodeKidsList(onto.situation)
  # т.к. в текущей ситуации нет ответа, а в параметрах при создании таблицы (БП) есть + 1 
  if len(situation_params) + 1 == ColCount:
  # т.к. в текущей ситуации нет ответа, а в параметрах при создании таблицы (БП) не сравниваем его
   for i in range(0,ColCount - 1):
    if request.form['ColName'+str(i)] not in situation_params:
     session['create_ontology_mistake'] = 'Ошибка создания БП. Загруженная модель БП не совпадает с введенными параметрами.'
     return redirect(url_for('ExpHandLoad.ExpHandLoad'))
  else:
   session['create_ontology_mistake'] = 'Ошибка создания БП. Загруженная модель БП не совпадает с введенными параметрами.'
   return redirect(url_for('ExpHandLoad.ExpHandLoad'))

 cur.execute('CREATE TABLE {0} (id integer primary key AUTO_INCREMENT{1})'.format(BPName, StrNames))
 cur.execute('CREATE TABLE {0} (id integer primary key AUTO_INCREMENT{1})'.format(DescriptionBPName, Description_Str_Names))
 cur.close()
 
 conn1 = get_db()
 cur_1 = conn1.cursor()
 conn2 = get_db()
 cur_2 = conn2.cursor()
 cur_1.execute('DESCRIBE {0}'.format(BPName))
 cur_2.execute('DESCRIBE {0}'.format(DescriptionBPName))
 TabInfo = cur_1.fetchall()
 DescriptionTabInfo = cur_2.fetchall()
 uploaded_files = ''
 if request.form.get('BPFile[]')!='' and request.form.get('CopyDataToBP')=='on':
  uploaded_files = request.files.getlist("BPFile[]")
 #CopyDataToBP(BPName, TextFile, TabInfo, request.files['BPFile'])
 # io.TextIOWrapper(request.files['BPFile'])
 if len(uploaded_files) == 1:
  print('CopyDataToBP1File!1')
  trainSize = request.form['TrainSizeInput']
  TextFile = io.TextIOWrapper(uploaded_files[0])
  CopyDataToBP1File(BPName, TextFile, TabInfo, trainSize)
 elif len(uploaded_files) == 2:
  print('CopyDataToBP1File!2')
  if uploaded_files[0].name.endswith('Train.csv') or uploaded_files[0].name.endswith('Train.txt'):
   TrainSample = io.TextIOWrapper(uploaded_files[0]).readlines()
   TestSample = io.TextIOWrapper(uploaded_files[1]).readlines()
  else:
   TestSample = io.TextIOWrapper(uploaded_files[0]).readlines()
   TrainSample = io.TextIOWrapper(uploaded_files[1]).readlines()
  CopySampleToBP(BPName, TrainSample, TabInfo, 'train')
  CopySampleToBP(BPName, TestSample, TabInfo, 'test')
 print('CopyDataToBP1File!3')
 cur_2.execute("show columns from {0}".format(DescriptionBPName))
 descr_values = [Row[1] for Row in cur_2.fetchall()]
 CopyDataToDescriptionTable(DescriptionBPName, StrDescNames, StrParamNames, StrDescriptions, StrTypes, StrUnits, StrRangeFrom, StrRangeTo, StrWeights, ColCount, descr_values)
 cur_1.execute('SELECT * FROM {0} ORDER BY id ASC'.format(BPName))
 cur_2.execute('SELECT * FROM {0} ORDER BY id ASC'.format(DescriptionBPName))
 TabData=cur_1.fetchall()
 TabDescrData = cur_2.fetchall()
 db = get_db()
 cur = db.cursor()
 cur.execute("SELECT table_name FROM information_schema.tables where table_schema='table_storage'\
				and table_name NOT LIKE '%Description' and table_name NOT LIKE 'users'")
 TabList = [Tab[0] for Tab in cur.fetchall()]
 return render_template('EditBP.html', TabList=TabList)
 #return render_template('DataWork.html', TabData=TabData, TabInfo=TabInfo, TabDescrData=TabDescrData, DescriptionTabInfo=DescriptionTabInfo)

def CopyDataToDescriptionTable(DescriptionBPName, StrDescNames ,StrParamNames, StrDescriptions, StrTypes, StrUnits, StrRangeFrom, StrRangeTo, StrWeights, ColCount, DescrTabInfTypes):
 #cur=get_db()
 conn=get_db()
 cur=conn.cursor()
 ParamNames_mas = StrParamNames[2:].split(', ')
 Descriptions_mas = StrDescriptions[2:].split(', ')
 Types_mas = StrTypes[2:].split(', ')
 Units_mas = StrUnits[2:].split(', ')
 RangeFrom_mas = StrRangeFrom[2:].split(', ')
 RangeTo_mas = StrRangeTo[2:].split(', ')
 Weights_mas = StrWeights[2:].split(', ')
 # flash(StrDescNames)
 for i in range(0,ColCount-1):
  mas_param = ParamNames_mas[i] + ', ' + Descriptions_mas[i]+ ', ' + Types_mas[i]+', ' + Units_mas[i]+', ' + RangeFrom_mas[i]+', ' + RangeTo_mas[i]+', ' + Weights_mas[i]
  mas_param_spl = mas_param.split(', ')
  DescrTabInfTypesNew = DescrTabInfTypes[1:]
  Buf=''
  #print(DescrTabInfTypesNew)
  #print(mas_param_spl)
  for j in range(0,len(mas_param_spl)-1):
   if DescrTabInfTypesNew[j] == 'text':
    Buf += "\'{}\', ".format(mas_param_spl[j])
   else:
    Buf += '{}, ' .format(mas_param_spl[j])
  Buf += mas_param_spl[len(mas_param_spl)-1]
  # flash(mas_param)
  cur.execute('INSERT INTO {0} ({1}) VALUES ({2})'.format(DescriptionBPName, StrDescNames, Buf))
 #db.commit()
 conn.commit()
 return

def CopyDataToBP1File(BPName, TextFile, TabInfo, trainSize):
 TextStr = TextFile.readlines() # массив строк
 RowsCount = len(TextStr)
 print(trainSize)
 print(RowsCount)
 CountTrainSize = math.ceil(RowsCount / 100 * int(trainSize,10))
 print('CountTrainSize' + str(CountTrainSize))
 print('RowsCount' + str(RowsCount))
 TrainSample, TestSample = GetSample(CountTrainSize, TextStr)
 CopySampleToBP(BPName, TrainSample, TabInfo, 'train')
 CopySampleToBP(BPName, TestSample, TabInfo, 'test')
 return
 
def GetSample(CountSampleSize, TextStr):
 Sample = []
 for i in range(0, CountSampleSize):
  randNumber = random.randint(0, len(TextStr)-1)
  print("randNumber " + str(randNumber))
  Sample.append(TextStr[randNumber])
  TextStr.pop(randNumber)
 return Sample, TextStr

def CopySampleToBP(BPName, TextRowsSample, TabInfo, SampleCode):
 print('CopySampleToBP')
 conn = get_db()
 db = conn.cursor()
 buf_types = []

 # dlya strok
 for tabinf in TabInfo[1:]:
  buf_types.append(tabinf[1])

 if (request.form.get('IdInFile') == 'on'):
  StrNames = ','.join(Str[0] for Str in TabInfo)
 else:
  StrNames = ','.join(Str[0] for Str in TabInfo[1:])  # начиная с 1 элемента
 for Str in TextRowsSample:
 #for i,Str in enumerate(TextStr):
  StrParam= re.split("[,; ]+", Str.replace('\n', ''))
  #Buf=', '.join('?' for s in StrParam)
  Buf=''
  for j,str_type in enumerate(StrParam):
   if buf_types[j] == 'varchar(255)':
    Buf += '\'{}\', '.format(str_type)
   else:
    Buf += '{}, '.format(str_type)
  Buf = Buf[0:len(Buf)-2]
  if SampleCode == 'train':
   db.execute("INSERT INTO {0} ({1}) VALUES ({2},\'{3}\','good')".format(BPName, StrNames, Buf, SampleCode))
  else:
   db.execute("INSERT INTO {0} ({1}) VALUES ({2},\'{3}\','')".format(BPName, StrNames, Buf, SampleCode))
  print(Buf)
 
 conn.commit()