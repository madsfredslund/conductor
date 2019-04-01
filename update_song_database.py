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

def update(table,params,values,id_name):
	"""
		@brief:	This function will updata a given table in the database with the above modified values"	
	"""
	tid = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
			
	############ INSERT/UPDATE heartbeat table #######################
	output = ''
	error = ''			
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		curr.execute("SELECT * FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s" % (table,table)) # There is nothing in this table yet!, db = "journal_site02"
		output = curr.fetchall()
		conn.commit()
		curr.close()
	except Exception, e:
		error = e

	if len(output) == 0 and error == '': # this should only occur once for every table if they are not deleted.
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		stmt = 'INSERT INTO %s %s VALUES %s' % (table, song_database_tables.return_list(table,"names"), song_database_tables.return_list(table,"values"))
		curr.execute(stmt)
		conn.commit()
		curr.close()
	
	if len(params) == len(values):
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		i = 0
		for parameter in params:
			if i > 0:
				parameters = parameters + ", " + str(parameter)
				ins_values = ins_values + ", " + str("'%s'" % values[i]) 
			else:
				parameters = str(parameter)
				ins_values = str("'%s'" % values[i])

			i += 1

		stmt = "UPDATE %s SET (%s, ins_at) = (%s, '%s') WHERE %s = (SELECT max(%s) FROM %s)" % (table, parameters, ins_values, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), id_name, id_name, table)
		curr.execute(stmt)		
		conn.commit()
		curr.close()
	
	else:
		print "An error occurred: ", error

	return 1

def update_old(table,params,values,id_name):
	"""
		@brief:	This function will updata a given table in the database with the above modified values"	
	"""
	tid = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
			
	############ INSERT/UPDATE heartbeat table #######################
	output = ''
	error = ''			
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		curr.execute("SELECT * FROM %s" % (table)) # There is nothing in this table yet!, db = "journal_site02"
		output = curr.fetchall()
		conn.commit()
		curr.close()
	except Exception, e:
		error = e

	if len(output) == 0 and error == '': # this should only occur once for every table if they are not deleted.
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		stmt = 'INSERT INTO %s %s VALUES %s' % (table, song_database_tables.return_list(table,"names"), song_database_tables.return_list(table,"values"))
		curr.execute(stmt)
		conn.commit()
		curr.close()
	
	if len(params) == len(values):
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		i = 0
		for parameter in params:
			stmt = "UPDATE %s SET %s = '%s' WHERE %s = (SELECT max(%s) FROM %s)" % (table, parameter, values[i], id_name, id_name, table)
			i +=1	
			curr.execute(stmt)
		stmt = "UPDATE %s SET ins_at = '%s' WHERE %s = (SELECT max(%s) FROM %s)" % (table, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), id_name, id_name, table)
		curr.execute(stmt)		
		conn.commit()
		curr.close()
	
	else:
		print "An error occurred: ", error

	return 1

def insert(table,params,values):
	"""
		@brief:	This function will insert a new row in a given table in the database"	
	"""
	tid = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())		
	############ INSERT/UPDATE heartbeat table #######################
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		stmt = 'INSERT INTO %s %s VALUES %s' % (table, params, values)               
		curr.execute(stmt)		
                conn.commit()
		curr.close()
	except Exception, e:
		print "An error occurred: ", e

	return 1

def delete(table):
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		curr.execute("DELETE FROM %s" % (table)) # There is nothing in this table yet!, db = "journal_site02"
		conn.commit()
		curr.close()
	except Exception, e:
		error = e

def print_newest_row(table):
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
		curr = conn.cursor()
		curr.execute("SELECT * FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s)" % (table,table)) # There is nothing in this table yet!, db = "journal_site02"
		conn.commit()
		output = curr.fetchall()
		curr.close()	
		for line in output:
			print line	
	except Exception, e:
		error = e

	
