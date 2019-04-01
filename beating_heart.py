import time
import psycopg2
import master_config as m_conf
import thread
import song_timeclass
import datetime

clock = song_timeclass.TimeClass()

host = m_conf.db_host
user = m_conf.db_user
db = m_conf.data_db
password = m_conf.db_password

def heartbeat(job_id):
	"""
		@brief:	This function will updata a given table in the database with the above modified values"	
	"""
	while True:
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password))
			curr = conn.cursor()
#			stmt = "UPDATE heartbeat SET (wall_clock) = ('%s') WHERE heartbeat_id = %i" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), int(job_id))
			stmt = "UPDATE heartbeat SET (wall_clock) = ('%s') WHERE heartbeat_id = %i" % (datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], int(job_id))
			curr.execute(stmt)		
			conn.commit()
			curr.close()
			conn.close()
		except Exception,e:
			print clock.whattime(), "Could not insert heartbeat into database..."
			print clock.whattime(), e

		time.sleep(60)	# The heart beats every minute.

def start_heartbeat(job_id):
	try:
		thread_value = thread.start_new_thread(heartbeat, (job_id,))
	except Exception,e:
		print clock.whattime(), e
	return 1
	

