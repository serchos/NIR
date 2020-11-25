import json

from flask import Blueprint, render_template, request
from config.db import get_db

bp = Blueprint('LookBP', __name__, url_prefix='/LookBP')

@bp.route('/', methods=('GET', 'POST'))
def LookBP():
	db = get_db()
	cur = db.cursor()
	cur.execute("SELECT table_name FROM information_schema.tables where table_schema='table_storage'\
				and table_name NOT LIKE '%Description' and table_name NOT LIKE 'users'")
	TabList=[Tab[0] for Tab in cur.fetchall()]
	return render_template('LookBP.html', TabList=TabList)
			
@bp.route('/Table=<string:TabName>/',  methods = ['GET', 'POST'])
def LookBPRequest(TabName):
	db = get_db()
	cur = db.cursor()
	BPName = request.args.get('TableChoice')
	Id = int(request.args.get('Id'), 10)
	
	if (Id == -1):
		cur.execute("SELECT COUNT(*) FROM {0}".format(BPName))
		TotalCount = cur.fetchone()[0]
		to_json = {'TotalCount' : TotalCount}
	else:
		CountStr = int(request.args.get('CountStr'), 10)
		cur.execute("SELECT COUNT(*) FROM {0} WHERE id>={1} AND id<{2}".format(BPName, Id, (Id+CountStr)))
		CurCount = cur.fetchone()[0]
		cur.execute('DESCRIBE {0}'.format(BPName))
		col_names = ''
		Info = cur.fetchall()
		for info in Info:
			col_names += info[0] + ','
  
		if (col_names != ''):
			col_names = col_names[:-1]
			col_names = col_names.replace(',sampleCode,qualityCode', '')
		print("SELECT {0} FROM {1} WHERE id>={2} AND id<{3}".format(col_names, BPName, Id, (Id+CountStr)))
		cur.execute("SELECT {0} FROM {1} WHERE id>={2} AND id<{3}".format(col_names, BPName, Id, (Id+CountStr)))
		TabData = cur.fetchall()
		to_json = {'Id' : Id, 'CurCount' : CurCount, 'TabData' : TabData}
	
	if (Id == 0):
		cur.execute('DESCRIBE {0}'.format(BPName))
		TabInfo = cur.fetchall()
		TabInfo = ModifyTabInfo(TabInfo) #Если это убрать, то поледние 2 колонки отображаются нормально
		cur.execute('DESCRIBE {0}'.format(BPName+'Description'))
		DescrTabInfo = cur.fetchall()
		cur.execute("SELECT * FROM {0}".format(BPName+'Description'))
		DescrTabData = cur.fetchall()
		to_json={'Id' : Id, 'CurCount' : CurCount, 'TabData' : TabData, 'TabInfo' : TabInfo, 'DescrTabData' : DescrTabData, 'DescrTabInfo' : DescrTabInfo}
	return json.dumps(to_json)

	
# удаляем 2 колонки из табинфо: выборка и качество
def ModifyTabInfo(Info):
	InfoList = list(Info)
	InfoList.pop()
	InfoList.pop()
	return tuple(InfoList)
	