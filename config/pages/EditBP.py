import json

from flask import Blueprint, render_template, request
from config.db import get_db
from modules.ImprovingEfficiencyAlgorithms import KMeans2, Classification2, TimurAlgorithm2


bp = Blueprint('EditBP', __name__, url_prefix='/EditBP')

@bp.route('/',  methods = ['GET', 'POST'])
def EditBP():
	db = get_db()
	cur = db.cursor()
	cur.execute("SELECT table_name FROM information_schema.tables where table_schema='table_storage'\
				and table_name NOT LIKE '%Description' and table_name NOT LIKE 'users'")
	TabList=[Tab[0] for Tab in cur.fetchall()]
	return render_template('EditBP.html', TabList=TabList)
	
	
#@bp.route('/DeleteBP',  methods = ['POST'])
@bp.route('/Delete/Tables=<string:TabNames>',  methods = ['GET', 'POST'])
def DeleteBP(TabNames):
	print("kek")
	db = get_db()
	cur = db.cursor()
	BPChoice=json.loads(request.values.get('BPChoice'))
	for BPName in BPChoice:
		cur.execute("DROP TABLE {0}".format(BPName))
		cur.execute("DROP TABLE {0}".format(BPName + 'Description'))
 
	db.commit()
	return 'OK'
 
 #все редактирование ?
#@bp.route('/EditBP',  methods = ['POST'])
@bp.route('/Edit/Table=<string:TabName>/',  methods = ['POST'])
def EditBPRequest(TabName):
	db = get_db()
	cur = db.cursor()
	BPName=request.values.get('TableChoice')
	cur.execute('DESCRIBE {0}'.format(BPName))
	TabInfo=cur.fetchall()
	buf_types= []
	#dlya strok
	for tabinf in TabInfo[1:]:
		buf_types.append(tabinf[1])
	Operation=request.values.get('Operation')
 
	if (Operation=='Delete'):
		Data=json.loads(request.values.get('JsonObj'))
		for Id in Data:
			cur.execute('DELETE FROM {0} WHERE id={1}'.format(BPName, Id))
		to_json={'Status': 'OK!'}
	elif Operation=='DeleteAll':
		cur.execute('DELETE FROM {0}'.format(BPName))
		to_json={'Status': 'OK!'}
	elif Operation=='Insert':
		CountStr=int(request.values.get('Count'), 10)
		RowId=[]
		for i in range(0, CountStr):
			cur.execute('INSERT INTO {0} () VALUES()'.format(BPName))
			cur.execute('SELECT last_insert_id()')
			RowId.append(cur.fetchone()[0])
		to_json={'LastInsertRowId': RowId}  
	elif Operation=='Update':
		Data=json.loads(request.values.get('JsonObj'))
		cur.execute('UPDATE {0} SET {1}="{2}" WHERE id={3}'.format(BPName, Data['ColName'], Data['Value'], Data['Id']))
		to_json={'Status': 'OK!'}
	elif Operation=='RenameColumn':
		Data=json.loads(request.values.get('JsonObj'))
		#db.execute('ALTER TABLE {0} RENAME COLUMN {1} TO {2}'.format(BPName, Data['ColName'], Data['Value']))
		to_json={'Status': 'OK!'}
	elif Operation=='Load From File':
		file=request.files['ImportBPFile']
		LastId=-1
		cur.execute("SELECT COUNT(*) FROM {0}".format(BPName))
		TotalCountBeforeInsert=cur.fetchone()[0]
		for line in file:
			line=re.sub("[\n\r]", "", line.decode('UTF-8'))
			data=re.split("[(,\s)(;\s),;\s]", line)
			#Buf=','.join('?' for d in data)
			Buf=''
			for j,data_type in enumerate(data):
				if buf_types[j] == 'varchar(255)':
					Buf += '\'{}\', '.format(data_type)
				else:
					Buf += '{}, '.format(data_type)
			Buf = Buf[0:len(Buf)-2]    

			cur.execute('INSERT INTO {0} VALUES(null, {1})'.format(BPName, Buf))
			if LastId==-1:
				#cur.execute("SELECT LAST_INSERT_ROWID()")
				cur.execute("SELECT last_insert_id()")
				LastId=cur.fetchone()[0]
  
		cur.execute("SELECT COUNT(*) FROM {0}".format(BPName))
		TotalCountAfterInsert=cur.fetchone()[0]

		to_json={'TCBI': TotalCountBeforeInsert, 'TCAI': TotalCountAfterInsert, 'LastId': LastId}

	conn.commit()
	return json.dumps(to_json)

#@bp.route('/ExportToFile',  methods = ['POST'])
@bp.route('/ExportToCSV/Table=<string:TabName>/',  methods = ['POST'])
def ExportToFile(TabName): 
	db = get_db()
	cur = db.cursor()
	BPName=request.form['HiddenTableChoice']
	tfile=tempfile.TemporaryFile()
	FileName=BPName
	#print(request.form['ExportToFile']) 

	if request.form['ExportToFile']=='Экспорт БП': 
		cur.execute("SELECT COUNT(*) FROM {0}".format(BPName))
		TotalCount, Id, CountStr=cur.fetchone()[0], 1, 5000

		while (Id<=TotalCount):
			cur.execute("SELECT * FROM {0} WHERE id>={1} AND id<{2}".format(BPName, Id, (Id+CountStr)))
			TabData=cur.fetchall()
  
			for Str in TabData:
				buf=','.join(str(Col) for Col in Str)+'\n'
				tfile.write(buf.encode("utf-8"))
 
			Id+=CountStr

	elif request.form['ExportToFile']=='Экспорт тестовой выборки':
		TestSample=request.form['HiddenTestSample']
		cur.execute('SELECT * FROM {0} WHERE id IN ({1})'.format(BPName, TestSample))
		TabData=cur.fetchall()
  
		for Str in TabData:
			buf=','.join(str(Col) for Col in Str)+'\n'
			tfile.write(buf.encode("utf-8"))
   
		FileName+='TestSample'
  
	elif request.form['ExportToFile']=='Экспорт обучающей выборки':
		TestSample=request.form['HiddenTestSample']
		cur.execute("SELECT COUNT(*) FROM {0}".format(BPName))
		TotalCount, Id, CountStr=cur.fetchone()[0], 1, 5000
 
		while (Id<=TotalCount):
			cur.execute("SELECT * FROM {0} WHERE id>={1} AND id<{2} AND id NOT IN ({3})".format(BPName, Id, (Id+CountStr), TestSample))
			TabData=cur.fetchall()
  
			for Str in TabData:
				buf=','.join(str(Col) for Col in Str)+'\n'
				tfile.write(buf.encode("utf-8"))
 
			Id+=CountStr
   
		FileName+='TrainSample'
 
	tfile.seek(0)
	return send_file(tfile, attachment_filename="{0}.csv".format(FileName), as_attachment=True, mimetype='text/csv')

#@bp.route('/RenameBP',  methods = ['POST'])
@bp.route('/Rename/Tables=<string:TabNames>',  methods = ['POST'])
def RenameBP(TabNames): 
	db = get_db()
	cur = db.cursor()
	cur.execute("SELECT table_name FROM information_schema.tables where table_schema='table_storage'\
				and table_name NOT LIKE '%Description'")
	OldBPNames=[BP[0] for BP in cur.fetchall()]
	NewBPNames=json.loads(request.values.get('NewBPNames'))
	for OldBPName, key in zip(OldBPNames,  range(0, len(NewBPNames))):
		try:
			cur.execute('ALTER TABLE {0} RENAME TO {1}'.format(OldBPName, NewBPNames.get(str(key))))
			cur.execute('ALTER TABLE {0}Description RENAME TO {1}Description'.format(OldBPName, NewBPNames.get(str(key))))
		except mysql.OperationalError:
			pass

	return 'OK'
	
@bp.route('/OptimizationBP',  methods = ['POST'])
def OptimizationBP():
	conn = get_db()
	cur = conn.cursor()
	BPName=request.values.get('TableChoice')
	OptArr=json.loads(request.values.get('JsonObj'))
	#print(BPName)
	cur.execute('SELECT * FROM {0} ORDER BY id ASC'.format(BPName))
	TabData=cur.fetchall()
	cur.execute('SELECT * FROM {0}Description ORDER BY id ASC'.format(BPName))
	DescrTabData=cur.fetchall()
	Weight=[Str[7] for Str in DescrTabData]

	if OptArr['OptAlgol']=='Classification':
		OptTabData=Classification2(TabData[:], OptArr['ClassMetric'], Weight, float(OptArr['ClassSimilarity']))	 
	elif OptArr['OptAlgol']=='KMeans':
		OptTabData=KMeans2(TabData, int(OptArr['KMClusterCount'], 10), OptArr['KMMetric'], Weight, OptArr['KMPrimaryCenter'])
	elif OptArr['OptAlgol']=='TimurAlgorithm':
		OptTabData=TimurAlgorithm2(TabData[:])
	'''
	if len(OptTabData)!=0:
		for Str in TabData:
			if (len(OptTabData)==0 or Str[0]!=OptTabData[0][0]):
				db.execute('DELETE FROM {0} WHERE id={1}'.format(BPName, Str[0]))
			else:
				OptTabData.pop(0)
	'''

	if len(OptTabData)!=0:
		#print(','.join(str(Str[0]) for Str in OptTabData))
		cur.execute('DELETE FROM {0} WHERE id NOT IN ({1})'.format(BPName, ','.join(str(Str[0]) for Str in OptTabData)))

	conn.commit()
	return 'Success'