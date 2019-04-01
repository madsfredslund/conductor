"""
Fetch ORs from db and execute them by running script

"""

import time
from song_daemonize import Daemon
import conductor_config as conf
import getopt
import daily_logging_handler
import sys
import datetime
import send_song_mail
import song_timeclass
import master_config as m_conf
import beating_heart
import selector
import check_ORs
import song_star_checker
import insertor
import updator
import check_daytime
import psycopg2
import get_db_values
import os
import psutil
import gc
import importlib

clock = song_timeclass.TimeClass()

def SigINTHandler(signum, frame):
	global RUNNING
	RUNNING = False
	return

def get_database_values(table_name, fields=[]):
	conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
	curr = conn.cursor()
	try:
		return_value = get_db_values.db_connection().get_fields(curr, table_name, fields)
	except Exception as e:
		conn.rollback()
		return_value = e
	curr.close()
     	conn.close() 
	return return_value

class CONDUCT(Daemon):
	"""
	Class inheriting the daemon-abilities from Daemon. Only run()-methods is overridden.
	"""
	
	def run(self):
		"""
		
		"""
		done_log_param = 0
		global RUNNING
		RUNNING = True

		#self.selector = selector.SELECTOR()
		#self.insertor = insertor
		self.sun_handle = song_star_checker.sun_pos(site=m_conf.song_site)	# Tenerife sun handle
		self.daily_update = 0
		self.daily_sun_insert = 0

		val = beating_heart.start_heartbeat(job_id=m_conf.conductor_id)

		over_all_obs_state = get_database_values(table_name='tel_dome', fields=['extra_param_1'])

		gc.disable()

		process = psutil.Process(os.getpid())
		print("Memory used in percent : %0.3f" % float(process.memory_percent()))
		mem = process.memory_info()
		mem_old = (float(mem.vms) / float(2 ** 20))

		print ""
		print clock.timename(), "The Conductor was started!\n"
		print clock.timename(), "The over all observing state was: ", over_all_obs_state['extra_param_1']

		while RUNNING:

			if int(float(datetime.datetime.strftime(datetime.datetime.utcnow(),"%H"))) < 9 and self.sun_handle.sun_alt(unit='f') < 0.0:
				yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
				folder_date = yesterday.strftime('%Y-%m-%d')
			else:
				folder_date = datetime.datetime.strftime(datetime.datetime.utcnow(),"%Y-%m-%d")

#			print "Checking the date: %s" % (str(folder_date))


			###################### DAY TIME CHECK ################################
			if int(float(datetime.datetime.strftime(datetime.datetime.utcnow(),"%H"))) < 10 and self.sun_handle.sun_alt(unit='f') > 1.0:
				try:
					daytime_obs = check_daytime.Check_Daytime(folder_date)
				except Exception,e:
					print clock.timename(), e
				else:
					if daytime_obs == 0 and self.daily_sun_insert == 0:
						print clock.timename(), "The Solar observations were not inserted yet. Will do now"
						try:
							#insertor.insert_solar_observations()
							insertor.insert_solar_observations_soda()
						except Exception,e:
							print clock.timename(), "Did not call the check-for-gaps function"
							print clock.timename(), e
						else:
							self.daily_sun_insert = 1 

				if conf.check_for_timecritical == "yes" and self.daily_update == 0:					
				
					st = datetime.datetime.utcnow()
					se = datetime.datetime.utcnow() + datetime.timedelta(days=1)
					try:
						selected_target = selector.SELECTOR().determine_next(timegap=[st,se], project_critical_type=["timecritical"])
					except Exception,e:
						print clock.timename(), "Problem in the selector.determine_next function..."
						print clock.timename(), e
					else:
						if selected_target != None:
							# Checking if they are already inserted:
							ids = []
							names = []
							for tmp_or in selected_target:
								ids.append(tmp_or[1])
								names.append(tmp_or[2])
							check_val = check_daytime.check_timecritical(folder_date,ids)
							if check_val == 0:
								for tcrit_target in selected_target:
									insertor.insert_timecritical_OR(pre_obs_spec_id=tcrit_target[1])	
								try:
									send_song_mail.send_mail().sending_an_email(reciever=["mads","frank"],sender="SONG_MS",subject="Time critical OR inserted",message="The conductor has inserted time critical OR(s) for the coming night.\nObject(s): %s\n" % str(names))
								except Exception,e:
									print "Could not send e-mail on time critical insertion..."				
					
					self.daily_update = 1
			
			###################### NIGHT TIME CHECK ################################
			try:
				gaps_in_ORs = check_ORs.check_for_gaps(folder_date)
#				print gaps_in_ORs
			except Exception,e:
				print clock.timename(), "Did not call the check-for-gaps function"
				print clock.timename(), e
			else:
				i = 1
				
				if len(gaps_in_ORs) > 0:
					#tmp_file = open("/tmp/conductor_targets.txt","w")
					#tmp_file.close()
					#tmp_file = open("/tmp/conductor_targets.txt","a")
					#tmp_file.write("# Possible targets to observe in the detected gap(s)\n# [%s]\n" % (str(gaps_in_ORs)))
					#tmp_file.write("\n# Object, Altitude at gap start, Priority\n")
					for gap in gaps_in_ORs:
						time_diff = gap[1] - gap[0]
						if float(time_diff.seconds) > 120 and gap[1] > gap[0]:
							try:
								print clock.timename(), "	-", i, "-	", gap[0].strftime("%Y-%m-%d %H:%M:%S"), "	", gap[1].strftime("%Y-%m-%d %H:%M:%S")
								i += 1
							except Exception,e:
								print clock.timename(), "	-", i, "-	", gap[0].strftime("%Y-%m-%d %H:%M:%S.%f"), "	", gap[1].strftime("%Y-%m-%d %H:%M:%S.%f")
								i += 1		
							try:
								selected_target = selector.SELECTOR().determine_next(timegap=gap, project_critical_type=conf.project_critical_type)
							except Exception,e:
								print clock.timename(), "Problem in the selector.determine_next function..."
								print clock.timename(), e
							

							if selected_target != None:
								print clock.timename(), "Selected target was: ", selected_target[2]
						
							over_all_obs_state = get_database_values(table_name='tel_dome', fields=['extra_param_1'])
							print clock.timename(), "The over all observing state was: ", over_all_obs_state['extra_param_1']

#							print clock.timename(), insertor.insert_OR(star_id=selected_target[0], gap=gap)
					#		print self.sun_handle.sun_alt(unit='f'), time_diff.seconds, selected_target, datetime.datetime.utcnow() + datetime.timedelta(seconds=int(120)), gap[0]
							if self.sun_handle.sun_alt(unit='f') < 0.0 and selected_target != None and datetime.datetime.utcnow() + datetime.timedelta(seconds=int(conf.insert_time_before)) > gap[0] and gap[1] > datetime.datetime.utcnow() and int(over_all_obs_state['extra_param_1']) in [0, 4, 6]:
								try:
									insertor.insert_OR(pre_obs_spec_id=selected_target[1], gap=gap)	
								except Exception,e:
									print clock.timename(), "Problem in the insertor.insert_OR function..."
									print clock.timename(), e


								print clock.timename(), "The Conductor would now have inserted an OR to fill the gap" 

					#	else:
					#		print clock.timename(), "	", "A gap of %i seconds was too small to care about..." % (int(time_diff.seconds))
					#		print clock.timename(), "	", gap[0].strftime("%Y-%m-%d %H:%M:%S.%f"), "	", gap[1].strftime("%Y-%m-%d %H:%M:%S.%f")
					#try:
					#	tmp_file.close()
					#except Exception, e:
					#	pass
					#try:
					#	exec_str = "scp /tmp/conductor_targets.txt madsfa@srf.prv:/var/www/new_web_site/conductor_targets.txt"
					#	os.popen(exec_str)
					#except Exception, e:
					#	print "Problem copying conductor targets to srf..."
					#	print e
				else:
					print clock.timename(), "The night looks to be perfectly covered!"
			

			if int(float(time.strftime("%H", time.gmtime()))) == 12 and done_log_param == 0:
				daily_logging_handler.handle_log_files(conf.outstream, conf.outstream_old)
				done_log_param = 1
			if done_log_param == 1 and int(float(time.strftime("%H", time.gmtime()))) > 12:
				done_log_param = 0
				self.daily_update = 0
				self.daily_sun_insert = 0


			process = psutil.Process(os.getpid())
			print("Memory used in percent : %0.3f" % float(process.memory_percent()))

			if float(process.memory_percent()) > 60:
				send_song_mail.send_mail().sending_an_email(reciever=["mads"],sender="SONG_MS",subject="Conductor using all memory!",message="The conductor has used more than 60 percent of the total memory on the song VM!\n\nPlease restart to clear memory ASAP!")
				os.system("python /home/madsfa/subversion/central_trunk/conductor/conductor.py -t ; python /home/madsfa/subversion/central_trunk/conductor/conductor.py -s")

			mem = process.memory_info()
			print "Memory used in MB: %.1f" % ((float(mem.vms) / float(2 ** 20)))
			print "Memory increase in MB: %.2f" % ((float(mem.vms) / float(2 ** 20)) - mem_old)
			mem_old = (float(mem.vms) / float(2 ** 20))

			gc.collect()

			if self.sun_handle.sun_alt(unit='f') > 5.0: # and int(float(datetime.datetime.strftime(datetime.datetime.utcnow(),"%H"))) >= 9:
				print clock.timename(), "Now sleeping for 10 minutes..."
				time.sleep(conf.daytime_sleep)	# sleeps for 10 minutes during daytime.
			else:
				time.sleep(conf.check_time)

			#### UPDATE active tables if needed!
			try:
				val = updator.update_ongoing_or()
			except Exception,e:
				print clock.timename(), "Error in the updator..."
				print clock.timename(), e
			
			#### UPDATE active tables if needed!
			try:
				val = updator.Update()
			except Exception,e:
				print clock.timename(), "Error in the updator..."
				print clock.timename(), e


			#print clock.timename(), "Restarting the Conductor"
			#os.system("python /home/madsfa/subversion/central_trunk/conductor/conductor.py -t ; python /home/madsfa/subversion/central_trunk/conductor/conductor.py -s")


def main():
	"""
	Parse command-line parameters, and start daemon
	"""



	daemon = CONDUCT(conf.pidfile, stdout=conf.outstream, stderr=conf.outstream)
	try:
		opts, list = getopt.getopt(sys.argv[1:], 'st')
	except getopt.GetoptError, e:
		print("Bad options provided!")
		sys.exit()

	for opt, a in opts:
		if opt == "-s":
			try:
				pid_number = open(conf.pidfile,'r').readline()
				if pid_number:
               				sys.exit('Daemon is already running!')
         		except Exception, e:
            			pass

			print("Starting daemon...!")
			daemon.start()
		elif opt == "-t":
			daemon.stop()
			print "The daemon is stoped!"
		else:
			print("Option %s not supported!" % (opt))



if __name__=='__main__':
	try:
		main()
	except Exception, e:
		print e
		print "The conductor has crashed at: ", clock.obstimeUT()
		send_song_mail.send_mail().sending_an_email(reciever=["mads"],sender="SONG_MS",subject="Conductor Crash!",message="The conductor daemon has crashed!\n\nCheck the log file to see why!\nLog onto hw as the user obs and type\nCheck the log file /home/obs/logs/conductor.log on central.")

#		send_song_mail.send_mail().send_sms(receiver=["Mads"], message="The conductor daemon was stopped for some reason. You got mail!")

