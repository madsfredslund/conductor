import time
import psycopg2
import datetime
import master_config as m_conf
import song_timeclass
import song_star_checker

clock = song_timeclass.TimeClass()
sun_handle = song_star_checker.sun_pos()

def select_ORs(date):
	start_time = str(sun_handle.sun_rise_pre()).replace("/", "-")
	stop_time = str(sun_handle.sun_set_next()).replace("/", "-")

	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()	
		curr.execute("SELECT object_name, start_window, stop_window, req_no, req_chain_previous FROM obs_request_1 WHERE start_window >= '%s' and stop_window <= '%s' AND stop_window > '%s' ORDER BY start_window ASC, req_prio DESC" % (str(start_time), str(stop_time), str(datetime.datetime.utcnow())))
		numb_of_rows = curr.rowcount
		output = curr.fetchall()
		return output, numb_of_rows
	except Exception,e:
		print e

	return 1	

def Check_Daytime(date):

	ready_ORs = select_ORs(date)
	
	if ready_ORs[1] == 0:
		# The daily Solar observations were not inserted into the database yet. 
		return 0
	elif ready_ORs[1] > 0: 
		i = 0
		for line in ready_ORs:
			try:
				for OR in line:
					if str(OR[0]).lower() == "sun":
						i += 1
			except Exception,e:
				pass
			
		if i > 0:
			return 1
		elif i == 0:
			return 0
		else:
			return 2

def check_timecritical(date, ids):

	ready_ORs = select_ORs(date)
	#print ready_ORs
	if ready_ORs[1] == 0:
		# No observations was entered yet
		return 0
	elif ready_ORs[1] > 0: 
		i = 0
		for line in ready_ORs:
			try:
				for OR in line:
					if OR[4] in ids:
						i += 1
			except Exception,e:
				pass
			
		if i > 0:
			return 1
		else:
			return 0		




