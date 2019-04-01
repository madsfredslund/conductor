# This updates status of specified table in the database.
import time
import psycopg2
import song_database_tables
import numpy
import master_config as m_conf

#host = "192.168.66.65"	# Tenerife site
#user = "postgres"
#db = "db_tenerife"
#password = ""
host = m_conf.db_host	# Tenerife site
user = m_conf.db_user
db = m_conf.data_db
password = m_conf.db_password

def get_fields(table_name, fields):

	field_str = ''
	for field in fields:
 		field_str += field
 		field_str += ','
	field_str = field_str[0:-1]

	conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
	curr = conn.cursor()
	stmt = 'SELECT %s FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s)' % (field_str, table_name, table_name)
	curr.execute(stmt)
	results = curr.fetchone()
	curr.close()
	res_dict = {}
	if results != None:
 		for i in range(len(results)):
    			res_dict[fields[i]] = results[i]
 		return res_dict
	else:
 		return None

def get_fields_with_id(table_name, fields, some_id, some_value):

	field_str = ''
	for field in fields:
 		field_str += field
 		field_str += ','
	field_str = field_str[0:-1]

	conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
	curr = conn.cursor()
	stmt = 'SELECT %s FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s WHERE %s = %s)' % (field_str, table_name, table_name, some_id, some_value)
	curr.execute(stmt)
	results = curr.fetchone()
	curr.close()
	res_dict = {}
	if results != None:
 		for i in range(len(results)):
    			res_dict[fields[i]] = results[i]
 		return res_dict
	else:
 		return None
