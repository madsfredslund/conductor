import time
import sys

sys.path.append("/home/madsfa/SONG/subversion/central_trunk/common/") 

import psycopg2
import central_song_checker
import conductor_config as conf
import datetime
import master_config as m_conf
import song_timeclass
import song_star_checker
import song_convert_coor
import check_ORs
import ephem
import central_song_checker
import song_checker_config
import numpy
import os
import socket
import gc
import psutil

clock = song_timeclass.TimeClass()
checker_handle = central_song_checker.Checker()

def twi_stop(time_stamp):

	song_site = ephem.Observer()
	song_site.lat = conf.lat_obs
	song_site.long = conf.long_obs
	song_site.elev = conf.elev_obs
	song_site.horizon = "%f:" % float(conf.obs_sun_alt)
	song_site.date = time_stamp

	sun = ephem.Sun()
	sun.compute(song_site)
	return song_site.next_rising(sun)

def moon_dist(star_ra, star_dec, time_stamp):
	"""
		@brief: This function calculates projected distance from the Moon to a given object on the sky.

		@param star_ra: The right ascension of a star given in the format: HH:MM:SS.
		@param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""        
	song_site = ephem.Observer()
	song_site.lat = conf.lat_obs
	song_site.long = conf.long_obs
	song_site.elev = conf.elev_obs
	song_site.date = time_stamp

	moon = ephem.Moon()
	moon.compute(song_site)

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')
	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec

	star.compute(song_site)
	m_d = ephem.separation(star, moon)
	moon_d = float(str(m_d).split(":")[0])
	return moon_d

class SELECTOR(object):
	"""
	@brief: This class will handle the more advanced scheduling for observing.
	"""
	def __init__(self):

		#gc.disable()
		#gc.enable()
		#gc.get_threshold
			
		self.check_handle = central_song_checker.Checker()	# Add posibility to select site to checker.
		self.check_star = song_star_checker.star_pos(site=conf.song_site)
		self.sun_handle = song_star_checker.sun_pos(site=conf.song_site)	# Tenerife sun handle
		self.hostname = socket.gethostname()

	def get_fields_time_int(self, curr, table_name, fields=[], time_int=0):
		field_str = ''
		for field in fields:
			field_str += field
			field_str += ','
		field_str = field_str[0:-1]
	
		stmt = "SELECT %s FROM %s WHERE ins_at > current_timestamp - INTERVAL '%s MINUTES'" % (field_str, table_name, str(time_int))
		curr.execute(stmt)
		results = curr.fetchall()

		res_dict = {}
		tmp_array = []
		for j in range(len(fields)):
			for i in range(len(results)):
				tmp_array.append(results[i][j])
			res_dict[fields[j]] = tmp_array
			tmp_array = []

		return res_dict


	def read_database(self, critical_type=""):
		"""
		@brief: Reading the database for relevant observations
		"""
		### Collect the 
		stars_data = []
		if conf.use_only_soda == "yes":
			try:
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
				curr = conn.cursor()
				curr.execute("SELECT starid, id, periodical_deltat, last_observed, schedule_type, exp_time, last_obs_attempt, last_req_no, ra, decl, object_name, project_priority, min_altitude, timecritical_tstart, timecritical_tend, vmag, slit, nr_exp FROM soda.pre_obs_req WHERE target_active = True AND active = True AND schedule_type = '%s' AND vmag IS NOT NULL AND starid > 0" % (str(critical_type)))
				stars_data = curr.fetchall()
				numb_of_rows = curr.rowcount
				print clock.timename(), "Number of targets to choose between: ", numb_of_rows
				curr.close()
				conn.close()
			except Exception, e:
				print clock.timename(), " Error: ", e
			else:
				#print "Size of object list from db: ", sys.getsizeof(stars_data)	
				return stars_data
		else:

			try:
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
				curr = conn.cursor()
				curr.execute("SELECT starid, pre_obs_spec_id, observe_every, last_observed, critical_type, exp_time, ins_at, last_ins_req_no FROM pre_obs_spec WHERE active = True AND critical_type = '%s' ORDER BY starid ASC" % (str(critical_type)))				
				obs_data = curr.fetchall()
				numb_of_rows = curr.rowcount
				curr.close()
				conn.close()
			except Exception, e:
				print clock.timename(), " Error: ", e
			else:
				if numb_of_rows > 0:
					starids = ""
					for line in obs_data:
						#print line
						starids = starids + str(line[0]) + ","
					starids = starids[:-1]

			
					try:
						conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
						curr = conn.cursor()
						curr.execute("SELECT ra, decl, object_name, starid FROM soda.stars WHERE starid IN (%s) ORDER BY starid ASC" % (str(starids)))
						stars_data = curr.fetchall()
						curr.close()
						conn.close()
					except Exception, e:
						print clock.timename(), " Error: ", e
					else:
						i = 0
						for line2 in stars_data:
							#print line2[-1], obs_data[i][0]
							if line2[-1] == obs_data[i][0] and line2[2].lower() != 'sun':
								obs_data[i] = obs_data[i] + line2[:-1]
							i +=1
							#print obs_data[i]
					### obs_data: starid, pre_obs_spec_id, observe_every, last_observed, critical_type, exp_time, ins_at, last_ins_req_no, ra, decl, object_name
					return obs_data
				else:
					print clock.timename(), "No stars were observable at this hour..."

		return []

	def check_status(self, req_no):

		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			curr.execute("SELECT status, ins_at FROM obs_request_status_1 WHERE req_no = %s" % (int(req_no)))
			req_status = curr.fetchone()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e
			return "error"	

		return req_status

	def check_objs(self, target_list=[], timegap=[]):
		"""
		@brief: This will check the altitude of the object
		"""
		return_list = []

		timestart = timegap[0]
		timestop = timegap[1]

		twilight_stop = datetime.datetime.strptime(str(twi_stop(timestart)), "%Y/%m/%d %H:%M:%S")

#		print target_list	


		# Read in wind data for the last 20 minutes...
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			wind_data = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "wxt520_wind_speed", "wxt520_wind_avgdir"], 20)	# search for high wind speeds in last 20 minutes
		except Exception, e:
			print clock.timename(), " Error: ", e
			high_wind = 0
			last_wind_dir = 0
		else:
			curr.close()
			conn.close()

			if len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_w_speed_flap)[0]) >= song_checker_config.wind_blow_events:
				high_wind = 1
				last_wind_dir = float(wind_data["wxt520_wind_avgdir"][-1])
			else:
				high_wind = 0
				last_wind_dir = 0
	
		for target_parameters in target_list:
		#	print target_parameters
			starid, pre_obs_spec_id, observe_every, last_observed, critical_type, exp_time, ins_at, last_ins_req_no, ra, decl, object_name, project_priority, min_altitude, timecritical_tstart, timecritical_tend, vmag, slit, nr_exp  = target_parameters

			#print object_name, vmag
			ra = ra / 15.

			seeing_check = 0
			obj_check = 0
			tel_min_alt = m_conf.telescope_min_altitude

			if critical_type != "timecritical":
				#print clock.timename(), "Checking object"

			#	process = psutil.Process(os.getpid())
			#	print("Mem 1 : ", process.memory_percent())

				obj_check = checker_handle.object_check2(ra, decl, high_wind, last_wind_dir, site=1)
			#	obj_check = 0
			#	process = psutil.Process(os.getpid())
			#	print("Mem 2 : ", process.memory_percent())
			
				if critical_type != "filler":
					if obj_check == 0:
						print clock.timename(), "%s is observable now" % (object_name)
					elif obj_check in [1,3]:
						print clock.timename(), "%s is too low in altitude now" % (object_name)
					elif obj_check  in [4,6]:
						print clock.timename(), "%s is too close to zenith now" % (object_name)
					elif obj_check == 2:
						print clock.timename(), "%s is observable now but wind speed is too high in that direction" % (object_name)

				if float(vmag) > m_conf.vmag_seeing_limit:
					objalt_f = float(self.check_star.star_alt_at(ra, decl, datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f"), unit="f"))
					#objalt_f = 50
					seeing_check = checker_handle.seeing_check(float(vmag),int(slit), alt=objalt_f)
					#seeing_check = 0
					#print clock.timename(), "seeing_check value: ", seeing_check
					try:
						if critical_type != "filler":
							if seeing_check == 1:
								print clock.timename(), "Seeing data was not up to date"
							elif seeing_check == 2:
								print clock.timename(), "Seeing was bad"
							elif seeing_check == 3:
								print clock.timename(), "No seeing data in search period"
							elif seeing_check == 0:
								clock.timename(), "The seeing was good for %s" % (object_name)
							else:
								clock.timename(), "Some other value was returned: ", seeing_check
					except Exception, e:
						print clock.timename(), " Error: ", e	

				if high_wind == 1:
					if critical_type != "filler":
						print clock.timename(), "Wind speed was too high for low targets"
					if critical_type in ["periodical", "largeprogram"] and int(nr_exp) > 5:
						tel_min_alt = conf.wind_alt_prime_limit
					else:
						tel_min_alt = conf.wind_alt_other_limit
				else:
					if critical_type != "filler":
						print clock.timename(), "Wind was fine"				
					tel_min_alt = m_conf.telescope_min_altitude

			else:
				tel_min_alt = m_conf.telescope_min_altitude
				obj_check = 0

			if critical_type == "timecritical":
				timestart_crit = timecritical_tstart + datetime.timedelta(milliseconds=1)
				timestop_crit = timecritical_tend + datetime.timedelta(milliseconds=1)

				objalt = str(self.check_star.star_alt_at(ra, decl, datetime.datetime.strptime(str(timestart_crit), "%Y-%m-%d %H:%M:%S.%f")))
				obj_alt = float(objalt.split(":")[0]) + float(objalt.split(":")[1]) / 60.  + float(objalt.split(":")[2]) / 3600.
				objalt2 = str(self.check_star.star_alt_at(ra,decl,datetime.datetime.strptime(str(timestart_crit), "%Y-%m-%d %H:%M:%S.%f")+datetime.timedelta(seconds=int(exp_time))))
				obj_alt2 = float(objalt2.split(":")[0]) + float(objalt2.split(":")[1]) / 60.  + float(objalt2.split(":")[2]) / 3600.

				moon_distance = moon_dist(ra, decl, datetime.datetime.strptime(str(timestart_crit), "%Y-%m-%d %H:%M:%S.%f"))

			else:
				objalt = str(self.check_star.star_alt_at(ra, decl, datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f")))
				obj_alt = float(objalt.split(":")[0]) + float(objalt.split(":")[1]) / 60.  + float(objalt.split(":")[2]) / 3600.
				objalt2 = str(self.check_star.star_alt_at(ra,decl,datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f")+datetime.timedelta(seconds=int(exp_time))))
				obj_alt2 = float(objalt2.split(":")[0]) + float(objalt2.split(":")[1]) / 60.  + float(objalt2.split(":")[2]) / 3600.
				moon_distance = moon_dist(ra, decl, datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f"))

			try:
				tmp = int(last_ins_req_no)
			except Exception,e:
				or_status = ["", ins_at]
				pass
			else:
				if int(last_ins_req_no) != 0:
					or_status = self.check_status(req_no = last_ins_req_no)
					if or_status == None:
						or_status = ["abort", ins_at]
					#print clock.timename(), "The status of the OR (%i) being checked was: %s" % (int(last_ins_req_no), str(or_status))

				else:
					or_status = ["done", ins_at]
			try:
				min_altitude = float(min_altitude)
			except Exception,e:
				if critical_type != "filler":
					print clock.timename(), "No minium altitude was set"
				min_altitude = 16.0

			
			time_diff = timestart - datetime.datetime.utcnow()
			#if time_diff.seconds > 600 and time_diff.days >= 0.0:
			#	print clock.timename(), "The time difference from utc-now and the gap was in seconds: ", time_diff.seconds
			#obj_check = 0



			if self.sun_handle.sun_alt(unit='f') > 0.0 or (obj_check == 1 and obj_alt > float(tel_min_alt)):
				obj_check = 0

			if critical_type == "timecritical":
				if float(obj_alt) > float(tel_min_alt) and float(obj_alt) < m_conf.max_alt_auto and float(obj_alt2) > float(tel_min_alt) and datetime.datetime.strptime(str(timestart_crit), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(exp_time)) < datetime.datetime.strptime(str(timestop_crit), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(2*60)) and datetime.datetime.strptime(str(timestart_crit), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(exp_time)) < twilight_stop and moon_distance > 5.0 and float(obj_alt) > float(min_altitude) and float(obj_alt2) > float(min_altitude) and timecritical_tstart >= datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") and timecritical_tend <= datetime.datetime.strptime(str(timestop), "%Y-%m-%d %H:%M:%S.%f"):
					prio = 100
				else:
					prio = 1

				to_return = starid, pre_obs_spec_id, object_name, obj_alt, prio, ra, decl
				#print to_return
				return_list.append(to_return)

			elif float(obj_alt) > float(tel_min_alt) and float(obj_alt) < m_conf.max_alt_auto and float(obj_alt2) < m_conf.max_alt_auto and float(obj_alt2) > float(tel_min_alt) and datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(exp_time)) < datetime.datetime.strptime(str(timestop), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(2*60)) and datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(exp_time)) < twilight_stop and obj_check == 0 and moon_distance > 5.0 and float(obj_alt) > float(min_altitude) and float(obj_alt2) > float(min_altitude) and seeing_check == 0:	# Allow observation to extend into next with 2 minutes - later 5 minutes in the actual insertion function - but not into twilight
				if last_observed != None and or_status[0] not in ["exec", "wait"] and int(last_ins_req_no) == 0 and critical_type in ["rv-standard", "periodical", "backup"]:
					### This target is observable and the priority will be calculated:
					#print clock.timename(), "%s last observed at: %s" % (object_name, last_observed)
					#timediff = datetime.datetime.utcnow() - last_observed
					timediff = datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") - last_observed
					#print clock.timename(), "Time diff: ", timediff
					prio = ((timediff.days + (timediff.seconds / 86400.)) / float(observe_every)) * 100.
				#	print prio
				elif or_status[0] == "done" and int(last_ins_req_no) != 0 and critical_type in ["rv-standard", "periodical", "backup"]: 
					### This target is observable and the priority will be calculated:
					#print clock.timename(), "%s last observed at: %s" % (object_name, ins_at)
					#timediff = datetime.datetime.utcnow() - last_observed
					timediff = datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") - last_observed
					#print clock.timename(), "Time diff: ", timediff
					prio = ((timediff.days + (timediff.seconds / 86400.)) / float(observe_every)) * 100.
				#	print prio
				elif or_status[0] == 'abort' and critical_type == 'filler':
					prio = 95
				elif or_status[0] == "exec" and critical_type in ["rv-standard", "periodical", "backup"]:
					prio = 1
				elif (or_status[0] == "exec" or (or_status[0] == "done" and int(last_ins_req_no) != 0)) and critical_type == 'filler': 
					prio = 1
				elif or_status[0] == "wait":
					prio = 1
				elif critical_type == 'filler':
					prio = 90 + (10.*(1./float(project_priority)))
				elif critical_type in ["rv-standard", "periodical", "backup"] and last_observed == None:

					try:
						month = datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f").month
						if int(month) >= 4 and int(month) < 10:
							ins_at = "%s-04-01" % (str(datetime.datetime.utcnow().year))
						elif int(month) >= 10:
							ins_at = "%s-10-01" % (str(datetime.datetime.utcnow().year))
						elif int(month) < 4:
							ins_at = "%s-10-01" % (str(datetime.datetime.utcnow().year - 1))
						timediff = datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") - datetime.datetime.strptime(str(ins_at), "%Y-%m-%d")
						print datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f")
						print datetime.datetime.strptime(str(ins_at), "%Y-%m-%d")
						prio = ((timediff.days + (timediff.seconds / 86400.)) / float(observe_every)) * 100.
					except Exception,e:
						print e
						prio = 100
				else:
					prio = 100
				#if prio > 100.: prio = 100
				to_return = starid, pre_obs_spec_id, object_name, obj_alt, prio, ra, decl
				#print to_return
				return_list.append(to_return)

			else:
				if critical_type != "filler":
					print clock.timename(), "Altitude, Time or Moon conditions are not allowing this object to be observed at the moment"
			#elif float(obj_alt) < float(m_conf.telescope_min_altitude) or float(obj_alt) > m_conf.max_alt_auto or float(obj_alt2) < float(m_conf.telescope_min_altitude):
			#	print "%s could not be observed because of the altitude: %s..." % (object_name, str(obj_alt))
			#elif datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(exp_time)) > datetime.datetime.strptime(str(timestop), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(2*60)) or datetime.datetime.strptime(str(timestart), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=int(exp_time)) > twilight_stop:
			#	print "%s could not be observed because of the time" % (object_name)
			#elif obj_check != 0:
			#	print "%s could not be observed because of the object check value: %i" % (object_name, obj_check)
			#elif moon_distance <= 5.0:
			#	print "%s too close to the Moon at this time" % (object_name)		

		gc.collect()

		return return_list

	def select_best(self, target_list, timestamp="", schedule_type=""):

		return_list = []
		if timestamp == "":
			timestamp = datetime.datetime.utcnow()
			timestamp2 = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
		else:
			timestamp2 = datetime.datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=60)

		for target_parameters in target_list:
			#print target_parameters
			starid, pre_obs_spec_id, object_name, obj_alt, prio, ra, decl = target_parameters
			objalt = str(self.check_star.star_alt_at(ra,decl,timestamp))
			obj_alt = float(objalt.split(":")[0]) + float(objalt.split(":")[1]) / 60.  + float(objalt.split(":")[2]) / 3600.

			#print str(timestamp), object_name, obj_alt, ra, decl

			objalt2 = str(self.check_star.star_alt_at(ra,decl,timestamp2))
			obj_alt2 = float(objalt2.split(":")[0]) + float(objalt2.split(":")[1]) / 60.  + float(objalt2.split(":")[2]) / 3600.

	#		print str(timestamp2), object_name, obj_alt, obj_alt2			

			if obj_alt - obj_alt2 < 0.0:
				if schedule_type != "filler":
					prio = prio * 0.95
				else:
					prio = prio + (10. / ((numpy.abs(obj_alt-50)+1)))	# prioritize object in an area where the pointing model is good.
			else:
				if schedule_type != "filler":
					prio = prio + (160. / obj_alt)	# This will add a value from 1 to 10 according to the altitude of the object. Prioritizing objects about to set.
				else:
					prio = prio + (20. / ((numpy.abs(obj_alt-50)+1)))	# prioritize object in an area where the pointing model is good.
				

			#if prio > 100.: prio = 100

			to_return = starid, pre_obs_spec_id, object_name, obj_alt, prio
			return_list.append(to_return)
			del to_return	

		return return_list

	def determine_next(self, timegap=[], project_critical_type=conf.project_critical_type):
		"""
		@brief: This is the primary function which will be called from the conductor.
		"""
		### If more than one project table is available (ToO's, semi-time-critical, observe_once)...

#		def send_to_srf():
#			#print self.hostname
#			if "srf" not in self.hostname:
#				print "copy to srf"
#				try:
#					exec_str = "scp /tmp/conductor_targets.txt madsfa@srf.prv:/var/www/new_web_site/conductor_targets.txt"
#					os.popen(exec_str)
#				except Exception, e:
#					print e
#			else:
#				print "On srf this will be executed..."
#				try:
#					exec_str = "scp /tmp/conductor_targets.txt /var/www/new_web_site/"
#					os.popen(exec_str)
#				except Exception, e:
#					print e	

		if "srf" in self.hostname:
			tmp_file = open("/var/www/new_web_site/conductor_targets.txt","w")
			tmp_file.close()	
		#	with open("/var/www/new_web_site/conductor_targets.txt", "a") as tmp_file:
		#		tmp_file.write("# Possible targets to observe in the detected gap\n# [%s, %s]\n" % (str(timegap[0]).split(".")[0], str(timegap[1]).split(".")[0]))
		#		tmp_file.write("\n# Object, Altitude at gap start, Priority\n")

	#	else:
	#		tmp_file = open("/tmp/conductor_targets.txt","a+")


		possible_targets = []
		possible_targets_2 = []
		for c_type in project_critical_type:

			print c_type
			possible_targets = self.read_database(critical_type=c_type)

			if len(possible_targets) > 0:
		
				possible_targets_2 = self.check_objs(target_list=possible_targets,timegap=timegap)

				if len(possible_targets_2) > 0:
								 
					def sort_by_prio(item):
						return item[4]

					sorted_target_list = sorted(possible_targets_2, key=sort_by_prio, reverse=True)

					if "srf" in self.hostname:
						with open("/var/www/new_web_site/conductor_targets.txt", "a") as tmp_file:
							tmp_file.write("# [%s, %s]\n" % (str(timegap[0]).split(".")[0], str(timegap[1]).split(".")[0]))
							tmp_file.write("# %s\n" % c_type)
							tmp_file.write("/\n")

					for t in sorted_target_list:
						if c_type != "filler":
							print t
						if "srf" in self.hostname:
							with open("/var/www/new_web_site/conductor_targets.txt", "a") as tmp_file:
								try:
									#tmp_file.write(str(t[2]).ljust(15)+str("%.2f" % t[3]).ljust(10)+str("%.2f" % t[4])+"\n")
									tmp_file.write(str(t[2]).replace(" ", "-")+str(" %.2f" % t[3])+str(" %.2f" % t[4])+"\n")
								except Exception,e:
									print e		
					

					#print possible_targets_2

					final_target_list = []
					highest_prio = sorted_target_list[0][4]
					for target in sorted_target_list:
						if target[4] == highest_prio:
							final_target_list.append(target)
						
					if c_type == "timecritical" and highest_prio == 100:
						return final_target_list
					elif c_type == "timecritical" and highest_prio < 100:
						return None

				#	for t in final_target_list:
				#		print t

					if c_type != "rv-standard":
						test_list = self.select_best(final_target_list, timestamp=timegap[0], schedule_type=c_type)

						def sort_by_prio(item):
							return item[4]

						sorted_target_list2 = sorted(test_list, key=sort_by_prio, reverse=True)
					else:
						sorted_target_list2 = final_target_list

					if c_type == "filler":
						for t in sorted_target_list2:
							print t

					#print sorted_target_list2
					final_target_list = []
					if len(sorted_target_list):
						final_target_list = []
						highest_prio = sorted_target_list2[0][4]
						for target in sorted_target_list2:
							if target[4] == highest_prio:
								final_target_list.append(target[:5])

					def sort_by_alt(item):
						return item[3]
	
					sorted_final_target_list = sorted(final_target_list, key=sort_by_alt, reverse=True)

					#if observable targets exists and the highest priority is grather than 90:  
					if len(sorted_final_target_list) > 0 and (sorted_final_target_list[0][-1] > 90 or c_type == "backup"):
						# Return the first object in the final list:
						#print clock.timename(), sorted_final_target_list[0]	
						#print str(timegap[0])

						return sorted_final_target_list[0]
					else:
						# No target was observable in this list of targets. 
						print  clock.timename(), "No targets was selected!"


	#	if "srf" in self.hostname:
	#		tmp_file.close()
	#	send_to_srf()
		return None
	


	def test_determine_next(self, pct=["periodical"]):
		
		print self.determine_next(timegap=[datetime.datetime.utcnow(), datetime.datetime.utcnow()+datetime.timedelta(days=1)], project_critical_type=pct)



















