import time
import sys

sys.path.append("/home/madsfa/SONG/subversion/central_trunk/common/") 

import song_star_checker
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
import datetime
import ephem
import sys
import psycopg2
import song_convert_coor
import master_config as m_conf
import os
import song_timeclass
import central_song_checker

clock = song_timeclass.TimeClass()
checker_handle = central_song_checker.Checker()

def check_for_gaps(date_of_night):
	"""
	@brief: This function is used when someone wants to see how the coming night will look if all goes well.
	"""


	o_star_path = "/" # Path to o-stars folder
	sys.path.append(o_star_path) 


	obs_lat = m_conf.lat_obs	# "28.2983" #latitude of the observatory
	obs_lon = m_conf.lon_obs	# "-16.5094" #longitude of the observatory with base "west"
	obs_elev = m_conf.elev_obs	# 2400 #elevation of the observatory

	host = m_conf.db_host
	db = m_conf.data_db
	or_db = m_conf.or_db
	user = m_conf.db_user
	password = m_conf.db_password

	def check_OR_status(req_no):

		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, db, user, password))
			curr = conn.cursor()	
			curr.execute("SELECT status, ins_at FROM obs_request_status_1 WHERE req_no = %s" % str(req_no))
			output = curr.fetchone()
			return output
		except Exception,e:
			print e

		return 1

	def get_all_or_night_data(date_of_night):

		start_time = "%s 15:00:00" % (str(date_of_night))
		stop_time = str(datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=1))

		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, or_db, user, password))
			curr = conn.cursor()	
#			curr.execute("SELECT right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, req_no, req_prio, obs_mode, constraint_5 FROM obs_request_1 WHERE start_window > '%s' and stop_window < '%s' order by req_prio desc" % (str(start_time), str(stop_time)))
			curr.execute("SELECT right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, req_no, req_prio, obs_mode, constraint_5, constraint_2, constraint_3, req_chain_next FROM obs_request_1 WHERE start_window > '%s' and stop_window < '%s' AND stop_window > '%s' ORDER BY start_window ASC, req_prio DESC" % (str(start_time), str(stop_time), str(datetime.datetime.utcnow())))
			output = curr.fetchall()
			return output
		except Exception,e:
			print e

		return 1
	
	def star_alt(star_ra, star_dec, time_stamp):
		"""
			@brief: This function will calculate the altitude of an object with given coordinates at a given time seem from Teide.

			@param star_ra: The right ascension of a star given in the format: HH:MM:SS.
			@param star_dec: The declination of a star given in the format: DD:MM:SS.
		"""       
		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.date = time_stamp

		star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')
		star.compute(song_site)
		alt_star = star.alt
		return alt_star

	def moon_alt(time_stamp):
		"""
		 @brief: This function calculates the altitude of the Moon.
		"""        
		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.date = time_stamp

		moon = ephem.Moon()
		moon.compute(song_site)
		return moon.alt

	def twi_start(time_stamp):

		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.horizon = "%f:" % float(m_conf.obs_sun_alt)
		song_site.date = time_stamp

		sun = ephem.Sun()
		sun.compute(song_site)
		return song_site.next_setting(sun)

	def twi_start_pre(time_stamp):

		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.horizon = "%f:" % float(m_conf.obs_sun_alt)
		song_site.date = time_stamp

		sun = ephem.Sun()
		sun.compute(song_site)
		return song_site.previous_setting(sun)

	def twi_stop(time_stamp):

		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.horizon = "%f:" % float(m_conf.obs_sun_alt)
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
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.date = time_stamp

		moon = ephem.Moon()
		moon.compute(song_site)
		star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')
		star.compute(song_site)
		m_d = ephem.separation(star, moon)
		return m_d

	   
	def sun_rise_pre(time_stamp):
		"""
		 @brief: This function will determine when the Sun has set last time.
		"""        
		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.date = time_stamp

		sun = ephem.Sun()
		sun.compute(song_site)
		return song_site.previous_rising(sun)

	def sun_rise_next(time_stamp):
		"""
		 @brief: This function will determine when the Sun has set last time.
		"""        
		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.date = time_stamp

		sun = ephem.Sun()
		sun.compute(song_site)
		return song_site.next_rising(sun)
	    
	def sun_set_pre(time_stamp):
		"""
		 @brief: This function will determine when the Sun sets next time.
		"""        
		song_site = ephem.Observer()
		song_site.lat = obs_lat
		song_site.long = obs_lon
		song_site.elev = obs_elev
		song_site.date = time_stamp

		sun = ephem.Sun()
		sun.compute(song_site)
		return song_site.previous_setting(sun)

	def get_fields(curr, table_name, fields=[], start_time='', stop_time=''):
		field_str = ''
		for field in fields:
			field_str += field
			field_str += ','
		field_str = field_str[0:-1]
	
		stmt = "SELECT %s FROM %s WHERE ins_at > '%s' AND ins_at < '%s' ORDER BY ins_at asc" % (field_str, table_name, str(start_time), str(stop_time))

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

##################################################################
#################### Script starts:
##################################################################

	t1 = time.time()

	time_stamp = "%s 23:00:00" % (str(date_of_night))

#	im_name = date_of_night.replace("-", "") + ".jpg"

#	print time_stamp
	time_stamp_2 = "%s/%s/%s 23:00:00" % (date_of_night.split("-")[0], date_of_night.split("-")[1], date_of_night.split("-")[2])

	try:
		start_time = datetime.datetime.strptime(str(sun_set_pre(time_stamp_2)), "%Y/%m/%d %H:%M:%S") + datetime.timedelta(milliseconds=1)
		stop_time = datetime.datetime.strptime(str(sun_rise_next(time_stamp_2)), "%Y/%m/%d %H:%M:%S") + datetime.timedelta(milliseconds=1)
	except Exception,e:
		print clock.timename(), e
		print clock.timename(), "Something with the times were wrong"

#	print "Start time: %s" % start_time
#	print "Stop time: %s" % stop_time

	try:
		twilight_start = datetime.datetime.strptime(str(twi_start(start_time)), "%Y/%m/%d %H:%M:%S") + datetime.timedelta(milliseconds=1)
		twilight_stop = datetime.datetime.strptime(str(twi_stop(start_time)), "%Y/%m/%d %H:%M:%S") + datetime.timedelta(milliseconds=1)
	except Exception,e:
		print clock.timename(), e
		print clock.timename(), "Something with the ast twilight times were wrong"

#	print "Twilight start: ", twilight_start
#	print "Twilight stop: ", twilight_stop

	delta_time_night = twilight_stop - twilight_start
	len_night = float(delta_time_night.seconds) / 3600.	# Convert to hours

	try:
		all_ors = get_all_or_night_data(date_of_night)
	except Exception,e:
		print clock.timename(), e
		print clock.timename(), "Something with the ast twilight times were wrong"

#	all_ors = numpy.array(all_ors)

	tmp_or_array = []

	tal = 0
#	print clock.timename(), "Order of ORs to be observed!"
	for OR in all_ors:
		or_status_output = check_OR_status(OR[7])
		or_status = or_status_output[0]
		or_status_ins_at = or_status_output[1]

		if or_status in ["wait", "exec"] and str(OR[2]).lower() != "sun":
		#	print clock.timename(), tal+1, OR
	#		print all_ors[tal]
	#		print (or_status,or_status_ins_at)
	#		print numpy.concatenate((numpy.array(OR), numpy.array(or_status,or_status_ins_at)), 0)
	#		print tuple(OR) + (or_status, or_status_ins_at)
			tmp_or_array.append(list(tuple(OR) + (or_status, or_status_ins_at)))
			#all_ors[tal] = tuple(OR) + (or_status, or_status_ins_at)
			#print all_ors[tal]
			tal += 1
		else:
			all_ors = numpy.delete(all_ors, (tal), axis=0)
		#	tmp_or_array = numpy.delete(all_ors, (tal), axis=0)


	all_ors = tmp_or_array

	if datetime.datetime.utcnow() > twilight_start:
		time_arr = [datetime.datetime.utcnow()]
	else:
		time_arr = [twilight_start]

	time_arr2 = []
	star_alt_arr = []
	moon_dist_arr = []
	moon_alt_arr = []
	objects = []
	obj_list = []
	exp_times = []
	start_over = 0	
	gaps_end = 0
	delay = 10
	readoutsec = 4	# Readouttime fraction in seconds	--- Full readouttime is "readouttime + (readoutms / 1000.)"
	readoutms = 210	# Readouttime fraction in miliseconds

	i = 0

	gaps = []
	obj_number = 1

	if len(all_ors) == 0 and datetime.datetime.utcnow() < twilight_stop - datetime.timedelta(seconds=180):
		print clock.timename(), "No night time ORs in database"
		if datetime.datetime.utcnow() < twilight_start:
			return [[twilight_start, twilight_stop]]
		else:
			return [[datetime.datetime.utcnow(), twilight_stop]]			

	elif datetime.datetime.utcnow() > twilight_stop and datetime.datetime.utcnow() < twilight_stop + datetime.timedelta(seconds=30):
		print clock.timename(), "Morning has come..."
		return []

	while time_arr[-1] < twilight_stop:

		line_number = 0

	#	print clock.timename(), "all_ors are of type: ", type(all_ors)

		for line in all_ors:

			
			#print time_arr[-1]

	#		t1 = time.time()
	#		or_status_output = check_OR_status(OR[7])
	#		or_status = or_status_output[0]
	#		or_status_ins_at = or_status_output[1]
	#		or_status = line[-2]
	#		or_status_ins_at = line[-1]

			set_to_delete = 0
			point_inserted = 0
			delay_ms = 0

			try:
				right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, OR_request_number, req_prio, obs_mode, o_star, numb_or_acq_exps, on_hold_time, multi_exp, or_status, or_status_ins_at  = line
			except Exception,e:
				print clock.timename(), "Could not get OR values"
				print clock.timename(), e

			if float(multi_exp) > 0:
				no_exp = int(multi_exp) * int(no_exp)

			### Check if observations about to be executed is troubled by high wind speeds.
			try:
				if or_status == "wait" and datetime.datetime.utcnow() > start_window and datetime.datetime.utcnow() < stop_window:
					#print clock.timename(), "For some reason OR: %s, Object: %s is not beeing executed..." % (OR_request_number,object_name)
					obj_check = checker_handle.object_check(right_ascension, declination, site=1)		##### HARDCODED SONGatOT
					#print clock.timename(), "Object and wind check values was: ", obj_check
					### Check returns 1 if object too low and 2 if wind is too high from object az direction and 3 if both are problematic.
					if obj_check == 2:
						#### Change start window to allow observations to start later on. 
						start_window = datetime.datetime.utcnow() + datetime.timedelta(minutes=20)	# 20 minutes which is the - on hold - time when wind is too high.
						try:
							all_ors[line_number][4] = start_window
						except Exception,e:
							print clock.timename(), "could not update the observing window with 20 minute delay"
							print clock.timename(), e
							try:
								all_ors[4] = start_window
							except Exception,e:
								print clock.timename(), "could not update the observing window with 20 minute delay with second try either"
								print clock.timename(), e
						print clock.timename(), "%s could not be observed at the moment because of high wind" % object_name
						break

					elif obj_check in [1,3]: # Object too low to be observed now.
						for index, item in enumerate(all_ors):	
							if object_name in item and OR_request_number in item:
								#print clock.timename(), "Deleting: ", object_name, OR_request_number
								line_number = index	
						#print clock.timename(), "%s too low and will not be observed" % object_name
						all_ors = numpy.delete(all_ors, (line_number), axis=0)
						set_to_delete = 0
						break	

					elif obj_check in [4,6]: # Object too close to zenith to be observed now.
						for index, item in enumerate(all_ors):	
							if object_name in item and OR_request_number in item:
								#print clock.timename(), "Deleting: ", object_name, OR_request_number
								line_number = index	
						all_ors = numpy.delete(all_ors, (line_number), axis=0)
						set_to_delete = 0
						break	
			except Exception,e:
				print clock.timename(), e			

#			if datetime.datetime.utcnow() >= twilight_start:
			if time_arr[-1] >= twilight_start:
				if or_status in ["wait", "exec"] and or_status_ins_at + datetime.timedelta(seconds=int(on_hold_time)*60) <= datetime.datetime.utcnow():

					#print datetime.datetime.utcnow(), time_arr[-1], object_name, start_window, stop_window, OR_request_number, numb_or_acq_exps

					if or_status == "exec":
						#print clock.timename(), time_arr[-1]
						#print clock.timename(), "Updating timestart with: ", or_status_ins_at
						time_arr[-1] = or_status_ins_at + datetime.timedelta(milliseconds=1)
		
					try:
						if start_window > time_arr[-1] and i == 0:
							gaps.append([time_arr[-1] + datetime.timedelta(milliseconds=1), start_window + datetime.timedelta(milliseconds=1)])
							time_arr.append(start_window + datetime.timedelta(milliseconds=1))
							i += 1
					except Exception,e:
						print clock.timename(), "could not create early gap"
						print clock.timename(), e

					if numb_or_acq_exps > 0:
						first_exposure = 1
					else:
						first_exposure = 0

					for exposure in range(no_exp):

						if first_exposure == 0:
							if obs_mode == "none-iodine":	
								delay = 120		# Add delay for ThAr, slewing and setup before star exposure.
							else:
								delay = 60		# Add delay for slewing and setup before star exposure.
							delay_ms = 0
						elif exposure+1 == no_exp:		
							if obs_mode == "none-iodine":	# Add delay if ThAr will be done after stars as well
								delay = 60
							else:
								delay = 5
							delay_ms = 0
						else:					# Add delays for reading out and saving spectrum
							delay = readoutsec
							delay_ms = readoutms

						if start_window < datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") and stop_window > datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") and datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(exp_time)) < twilight_stop + datetime.timedelta(seconds=float(5*60)):
							if float(str(star_alt(right_ascension, declination, datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(exp_time)))).split(":")[0]) > 15 and float(str(star_alt(right_ascension, declination, datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(exp_time)))).split(":")[0]) < m_conf.max_alt_auto:
								time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(exp_time)+float(delay), milliseconds=delay_ms))
							else:
								set_to_delete = 1
								#print clock.timename(), "%s was too low at: %s" % (object_name,str(time_arr[-1]))
								break
						elif stop_window < datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f"): 	
							for index, item in enumerate(all_ors):	
								if object_name in item and OR_request_number in item:
									#print clock.timename(), "Deleting: ", object_name, OR_request_number
									line_number = index	
							#print clock.timename(), "Deleting 1 line number: ", line_number
							all_ors = numpy.delete(all_ors, (line_number), axis=0)
							set_to_delete = 0
							break
						else:
							break

						first_exposure = 1					
						set_to_delete = 1

					if set_to_delete == 1 and len(all_ors) > 0:	
						try:
							for index, item in enumerate(all_ors):	
								if object_name in item and OR_request_number in item:
									#print clock.timename(), "Deleting: ", object_name, OR_request_number
									line_number = index	
							#print clock.timename(), "Deleting 2 line number: ", line_number	
							all_ors = numpy.delete(all_ors, (line_number), axis=0)
							set_to_delete = 0
							point_inserted = 1
						except Exception,e:
							print clock.timename(), "Could not delete OR from array"
							print clock.timename(), e
						break

					line_number += 1

				else:
					for index, item in enumerate(all_ors):	
						if object_name in item and OR_request_number in item:
							#print clock.timename(), "Deleting: ", object_name, OR_request_number
							line_number = index	
					#print clock.timename(), "Deleting 3 line number: ", line_number	
					all_ors = numpy.delete(all_ors, (line_number), axis=0)
					line_number += 1
					break

				if point_inserted == 0 and line_number == len(all_ors):	
					delay = 10
					if len(gaps) > 0 and time_arr[-1] < twilight_stop:	
						if time_arr[-1] == gaps[-1][1] and datetime.datetime.utcnow() < gaps[-1][0]:
							gaps[-1][1] = gaps[-1][1] + datetime.timedelta(seconds=float(delay), milliseconds=delay_ms)
						elif time_arr[-1] == gaps[-1][1] and datetime.datetime.utcnow() >= gaps[-1][0]:
							gaps[-1][1] = gaps[-1][1] + datetime.timedelta(seconds=float(delay), milliseconds=delay_ms)
							gaps[-1][0] = datetime.datetime.utcnow()
						else:
							gaps.append([datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f"), datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(delay), milliseconds=delay_ms)])
					else:
						if time_arr[-1] < twilight_stop:
							gaps.append([datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f"), datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(delay), milliseconds=delay_ms)])

					time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(seconds=float(delay), milliseconds=delay_ms))

			else:
				return []

#			print time.time() - t1

		
		if len(all_ors) == 0 and time_arr[-1] < twilight_stop and gaps_end == 0:
			gaps.append([datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S.%f"), twilight_stop + datetime.timedelta(milliseconds=1)])
			gaps_end = 1 
			break

		i += 1
		if i == 5000:
			print clock.timename(), "i = 5000"
			break

	return gaps
