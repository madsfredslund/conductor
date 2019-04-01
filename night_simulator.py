import time
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
import selector


def create_theory_obs_plot_soda(date_of_night):
	"""
	@brief: This function is used when someone wants to see how the coming night will look if all goes well.
	"""


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
			curr.execute("SELECT status FROM obs_request_status_1 WHERE req_no = %s" % str(req_no))
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
			curr.execute("SELECT right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, req_no, req_prio, obs_mode, constraint_5 FROM obs_request_1 WHERE start_window > '%s' and stop_window < '%s' AND LOWER(object_name) != 'sun' order by req_prio desc, start_window asc " % (str(start_time), str(stop_time)))
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
		moon_d = float(str(m_d).split(":")[0])
		return moon_d

	   
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

	def get_or_data(pre_obs_req_id):
		
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
			curr = conn.cursor()	
			curr.execute("SELECT obs_mode, exp_time, nr_exp, nr_target_exp, object_name, ra, decl FROM soda.pre_obs_req WHERE id = %s" % str(pre_obs_req_id))
			output = curr.fetchone()
			return output
		except Exception,e:
			print e

		return 1

	def get_conductor_target(timestamp):

#################### Script stars:

	db_data = 0

	print date_of_night

	try:
		im_name = str(int(date_of_night))
	except Exception,e:
		print "The data does not come from a file but the script will check the database..."
		db_data = 1
		im_name = date_of_night.replace("-", "") + ".jpg"

	if db_data == 0:

		obs_requests = []

		i = 1

		for line in ors_to_check:
			print line.split(" ")
			if len(line.split(" ")) > 3:

				try:
					pre_obs_req_id, win_start, win_stop, req_prio, obs_mode, nr_exp, o_star = line.strip("\n").split(" ")
				except Exception,e:
					pre_obs_req_id, win_start, win_stop, req_prio, obs_mode, nr_exp = line.strip("\n").split(" ")
					o_star = ""

				obs_request_config = get_or_data(int(pre_obs_req_id))

				try:
					obs_requests.append([float(obs_request_config[5]) / 15., float(obs_request_config[6]), obs_request_config[4], int(obs_request_config[1]), win_start.replace("T", " "), win_stop.replace("T", " "), int(nr_exp), i, int(req_prio), obs_mode, o_star])
				except Exception,e:
					print e	
				i += 1		

		def sort_by_win_start(item):
			return item[4]

		def sort_by_prio(item):
			return item[8]

#		obs_requests = sorted(obs_requests, key=sort_by_win_start)

		obs_requests = sorted(obs_requests, key=sort_by_prio, reverse=True)

		print obs_requests

		print float(str(obs_requests[0][4]).split(" ")[1][0:2])
		if float(str(obs_requests[0][4]).split(" ")[1][0:2]) < 12:
			print str(obs_requests[0][4]).split(" ")[0]
			date_of_night = datetime.datetime.strptime(str(obs_requests[0][4]).split(" ")[0], "%Y-%m-%d") - datetime.timedelta(days=1)
			date_of_night = str(date_of_night).split(" ")[0]
		else:
			date_of_night = obs_requests[0][4].split(" ")[0]


		#### Reading already inserted data for this night: obs_mode, exp_time, nr_exp, nr_target_exp, object_name, ra, decl
		db_DATA = get_all_or_night_data(date_of_night)
		
		for line in db_DATA:
			print line
			try:
				right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, req_no, req_prio, obs_mode, o_star = line
			except Exception,e:
				print e
			else:

				try:
					obs_requests.append([float(right_ascension), float(declination), object_name, int(exp_time), start_window, stop_window, int(no_exp), i, int(req_prio), obs_mode, o_star])
				except Exception,e:
					print e	
				i += 1		

		def sort_by_win_start(item):
			return item[4]

		def sort_by_prio(item):
			return item[8]

#		obs_requests = sorted(obs_requests, key=sort_by_win_start)

		obs_requests = sorted(obs_requests, key=sort_by_prio, reverse=True)



	print date_of_night

	time_stamp = "%s 23:00:00" % (str(date_of_night).strip("'"))

	print time_stamp
	time_stamp_2 = "%s/%s/%s 23:00:00" % (date_of_night.split("-")[0].strip("'"), date_of_night.split("-")[1].strip("'"), date_of_night.split("-")[2].strip("'"))
	print time_stamp_2

	try:
		start_time = datetime.datetime.strptime(str(sun_set_pre(time_stamp_2)), "%Y/%m/%d %H:%M:%S")
		stop_time = datetime.datetime.strptime(str(sun_rise_next(time_stamp_2)), "%Y/%m/%d %H:%M:%S")
	except Exception,e:
		print e
		print "Something with the times were wrong"

	print "Start time: %s" % start_time
	print "Stop time: %s" % stop_time
	
	try:
		twilight_start = datetime.datetime.strptime(str(twi_start(start_time)), "%Y/%m/%d %H:%M:%S")
		twilight_stop = datetime.datetime.strptime(str(twi_stop(start_time)), "%Y/%m/%d %H:%M:%S")
	except Exception,e:
		print e
		print "Something with the ast twilight times were wrong"

	print "Twilight start: ", twilight_start
	print "Twilight stop: ", twilight_stop

	delta_time_night = twilight_stop - twilight_start
	len_night = float(delta_time_night.seconds) / 3600.	# Convert to hours

	if db_data == 1:
		try:
			all_ors = get_all_or_night_data(date_of_night)
		except Exception,e:
			print e	
		else:
			all_ors = numpy.array(all_ors)
	else:
		all_ors = numpy.array(obs_requests)

	time_arr = []
	time_arr2 = []
	star_alt_arr = []
	moon_dist_arr = []
	moon_alt_arr = []
	objects = []
	obj_list = []
	exp_times = []
	set_to_delete = 0
	start_over = 0	

	delay = 10

	i = 0

	#print all_ors




	plt.figure(figsize=(9.0, 6.0),facecolor='w', edgecolor='k')
	plt.subplots_adjust(left=0.08, bottom=0.08, right=0.80, top=0.93, wspace=0.4, hspace=0.3)

	ax=plt.subplot(111)
	daysFmt=matplotlib.dates.DateFormatter("%H") 
	ax.xaxis.set_major_formatter(daysFmt) 

	print "Number of ORs: ", len(all_ors)
	obj_number = 1

	while len(all_ors) > 0:

#		for or_line in all_ors:	
#			print or_line

		line_number = 0
		for line in all_ors:

			print "Length of all_ors: ", len(all_ors)

			if db_data == 1:
				or_status = check_OR_status(line[7])
				OR_request_number = line[7]

				print "Status of OR %s was: %s" % (str(line[7]), str(or_status))
			else:
				or_status= ["wait"]

			point_inserted = 0

			try:
				print datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S")
			except Exception,e:
				pass


			if or_status[0] != "abort":			

				try:
					right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, req_no, req_prio, obs_mode, o_star = line
				except Exception,e:
					print e

				exp_time = int(exp_time)
				no_exp = int(no_exp)
				req_no = int(req_no)	
				OR_request_number = req_no			
				req_prio = int(req_prio)	

				start_window = str(start_window).strip("'")
				stop_window = str(stop_window).strip("'")
				try:
					start_window = datetime.datetime.strptime(str(start_window), "%Y-%m-%d %H:%M:%S")
					stop_window = datetime.datetime.strptime(str(stop_window), "%Y-%m-%d %H:%M:%S")
				except Exception,e:
					print "hejsa"
					print e

				print right_ascension, declination, object_name, exp_time, start_window, stop_window, no_exp, req_no, req_prio, obs_mode, o_star

		#		try:
		#			object_name = object_name.replace(" ", "")
		#		except Exception,e:
		#			print e

				new_time_arr = []
				new_star_alt_arr = []

				if obs_mode.lower() == "template" and o_star + "_o-star.py" in os.listdir("/var/www/o_stars/"):
					o_star_config = __import__(str(o_star + "_o-star"))					
					print "Calculating the o-star...", o_star
					first_exposure = 0
					for exposure in range(o_star_config.ostar_num_exp):
						if first_exposure == 0:
							delay = 120
						else:
							delay = 2

						if len(time_arr) == 0:
							if start_window < twilight_start and stop_window > twilight_start:
								if twilight_start + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) < stop_window:
									if float(str(star_alt(o_star_config.ostar_ra_hours, o_star_config.ostar_dec_degrees, twilight_start + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)))).split(":")[0]) > 15 and moon_dist(o_star_config.ostar_ra_hours, o_star_config.ostar_dec_degrees, twilight_start) > 5:
										time_arr.append(twilight_start + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) + datetime.timedelta(seconds=float(delay)))
										new_time_arr.append(twilight_start)
										new_time_arr.append(twilight_start + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) + datetime.timedelta(seconds=float(delay)))
									else:
										print "The o-star was not above 15 degrees...twilight"
										break
								else:
									print "The o-star will not finish before stop window...twilight"
									break
							else:
								print "We were not in the obs window of the o-star...twilight"
								break
						else:

							if start_window < datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") and stop_window > datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S"):
								if datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) < stop_window and datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) < twilight_stop:
									if float(str(star_alt(o_star_config.ostar_ra_hours, o_star_config.ostar_dec_degrees, datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)))).split(":")[0]) > 15 and moon_dist(o_star_config.ostar_ra_hours, o_star_config.ostar_dec_degrees, twilight_start) > 5:
										time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) + datetime.timedelta(seconds=float(delay)))
										new_time_arr.append(datetime.datetime.strptime(str(time_arr[-2]), "%Y-%m-%d %H:%M:%S"))
										new_time_arr.append(datetime.datetime.strptime(str(new_time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(o_star_config.ostar_exptime_spec)) + datetime.timedelta(seconds=float(delay)))
									else:
										print "The o-star was not above 15 degrees..."
										break
								else:
									print "The o-star will not finish before stop window..."
									break
							else:
								print "We were not in the obs window of the o-star..."
								break

						try:
							star_alt_val = star_alt(o_star_config.ostar_ra_hours, o_star_config.ostar_dec_degrees, time_arr[len(time_arr)-1])
							print star_alt_val
							star_altitude = float(str(star_alt_val).split(":")[0]) + float(str(star_alt_val).split(":")[1]) / 60. + float(str(star_alt_val).split(":")[2]) / 3600.

							star_alt_val2 = star_alt(right_ascension, declination, new_time_arr[len(new_time_arr)-2])
							print star_alt_val2
							star_altitude2 = float(str(star_alt_val2).split(":")[0]) + float(str(star_alt_val2).split(":")[1]) / 60. + float(str(star_alt_val2).split(":")[2]) / 3600.
						except Exception,e:
							print e
							print "Could not get star altitude"

						try:
							if o_star_config.ostar_name + " " + "Template" not in objects:
								objects.append(o_star_config.ostar_name + " " + "Template")
						except Exception,e:
							print e
							print "Could not append some coordinate thing"

						new_star_alt_arr.append(star_altitude2)
						new_star_alt_arr.append(star_altitude)
						star_alt_arr.append(star_altitude)
						exp_times.append(o_star_config.ostar_exptime_spec)

						if first_exposure == 0:
							try:
								plt.plot_date(new_time_arr, new_star_alt_arr, '-b')
								plt.plot_date(new_time_arr, numpy.ones((len(new_time_arr))), '-k', linewidth=3)
							except Exception,e:
								print e	

						first_exposure = 1
					
						set_to_delete = 1

					try:
						plt.plot_date(new_time_arr[1:], new_star_alt_arr[1:], '-b*')
						plt.plot_date(new_time_arr[1:], numpy.ones((len(new_time_arr[1:]))), '-k', linewidth=3)
					except Exception,e:
						print e

				if obs_mode.lower() == "template" and first_exposure == 0:
					#print "o-star was not observable and the template will not be observed..."
					#print "Deleting aborted object: ", line[2]
					#all_ors = numpy.delete(all_ors, (line_number), axis=0)
					#line_number += 1
					#break
					star_alt_arr.append(-50)
					if len(time_arr) == 0:
						time_arr.append(twilight_start + datetime.timedelta(seconds=float(delay)))
					else:
						time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(delay)))
					break

				first_exposure = 0
				for exposure in range(no_exp):
					moon_too_close = 0
					if first_exposure == 0:
						delay = 120
					else:
						delay = 2
					if len(time_arr) == 0:
						try:
							if start_window < twilight_start and stop_window > twilight_start:
								if twilight_start + datetime.timedelta(seconds=float(exp_time)) < stop_window:
									if float(str(star_alt(right_ascension, declination, twilight_start + datetime.timedelta(seconds=float(exp_time)))).split(":")[0]) > 15:
										time_arr.append(twilight_start + datetime.timedelta(seconds=float(exp_time)) + datetime.timedelta(seconds=float(delay)))
										new_time_arr.append(twilight_start)
										new_time_arr.append(twilight_start + datetime.timedelta(seconds=float(exp_time)) + datetime.timedelta(seconds=float(delay)))
									else:
										break
								else:
									break
							else:
								break
						except Exception,e:
							print e		
					else:
						try:
							if start_window < datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") and stop_window > datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S")  and datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(exp_time)) < twilight_stop:
								if datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(exp_time)) < stop_window:
									if float(str(star_alt(right_ascension, declination, datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(exp_time)))).split(":")[0]) > 15 and moon_dist(right_ascension, declination, datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S")) > 5:
										time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(exp_time)) + datetime.timedelta(seconds=float(delay)))
										new_time_arr.append(datetime.datetime.strptime(str(time_arr[-2]), "%Y-%m-%d %H:%M:%S"))
										new_time_arr.append(datetime.datetime.strptime(str(new_time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(exp_time)) + datetime.timedelta(seconds=float(delay)))
									elif moon_dist(right_ascension, declination, datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S")) < 5:
										moon_too_close = 1
										if object_name + " - close Moon" not in obj_list:
											obj_list.append(object_name + " - close Moon")
											print obj_list
									else:
										break
								else:
									break
							elif stop_window < datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S"): 	
								match = 0
								for index, item in enumerate(all_ors):
									
									if object_name in item and int(OR_request_number) == int(item[7]):
										match = 1
										line_number = index
								if match == 0:
									print ".... NO MATCH ...."
								print "Deleting line number - %i - because of exceeded stop time for object: %s" % (line_number, object_name)

								all_ors = numpy.delete(all_ors, (line_number), axis=0)
								#if len(all_ors) == 1:
								#	all_ors = numpy.delete(all_ors, (0), axis=0)
								#else:
								#	all_ors = numpy.delete(all_ors, (line_number), axis=0)
								break
							else:
								break
						except Exception,e:
							print e	

					if moon_too_close == 0:
						try:
							star_alt_val = star_alt(right_ascension, declination, time_arr[len(time_arr)-1])
							star_altitude = float(str(star_alt_val).split(":")[0]) + float(str(star_alt_val).split(":")[1]) / 60. + float(str(star_alt_val).split(":")[2]) / 3600.

							star_alt_val2 = star_alt(right_ascension, declination, new_time_arr[len(new_time_arr)-2])
							star_altitude2 = float(str(star_alt_val2).split(":")[0]) + float(str(star_alt_val2).split(":")[1]) / 60. + float(str(star_alt_val2).split(":")[2]) / 3600.
						except Exception,e:
							print e
							print "Could not get star altitude"

	#					if obs_mode.lower() == "iodine":
	#						mode_to_plot = "i2"
	#					elif obs_mode.lower() == "none-iodine":
	#						mode_to_plot = "ThAr"
	#					elif obs_mode.lower() == "template":
	#						mode_to_plot = "Template"
	#					try:
	#						if object_name + " " + mode_to_plot not in objects:
	#							objects.append(object_name + " " + mode_to_plot)
	#					except Exception,e:
	#						print e
	#						print "Could not append some coordinate thing"
						new_star_alt_arr.append(star_altitude2)
						new_star_alt_arr.append(star_altitude)
						star_alt_arr.append(star_altitude)
						exp_times.append(exp_time)

						if first_exposure == 0:
							try:
								plt.plot_date(new_time_arr, new_star_alt_arr, '-b')
								plt.plot_date(new_time_arr, numpy.ones((len(new_time_arr))), '-k', linewidth=3)
							except Exception,e:
								print e	

					first_exposure = 1
				
					set_to_delete = 1
				if set_to_delete == 1:	
					try:
						line_number = 0
						for index, item in enumerate(all_ors):
							if int(OR_request_number) == int(item[7]):
								line_number = index
						print "Deleting object: %s, line_number: %s, OR_number: %s" % (str(line[2]), str(line_number), str(OR_request_number))	
						#print "Deleting line number: ", line_number
						print all_ors[line_number] 
						all_ors = numpy.delete(all_ors, (line_number), axis=0)
						#all_ors = numpy.delete(all_ors, (line_number), axis=0)
						set_to_delete = 0
						point_inserted = 1
					except Exception,e:
						print e
					break

				line_number += 1

			else:
				for index, item in enumerate(all_ors):	
					if object_name in item and int(OR_request_number) == int(item[7]):
						#print index
						line_number = index	
				print "Deleting aborted object: ", object_name
				all_ors = numpy.delete(all_ors, (line_number), axis=0)
				#print "Deleting aborted object: ", line[2]
				#all_ors = numpy.delete(all_ors, (line_number), axis=0)
				line_number += 1
				break

			if point_inserted == 0 and line_number == len(all_ors):
				star_alt_arr.append(-50)
				if len(time_arr) == 0:
					time_arr.append(twilight_start + datetime.timedelta(seconds=float(delay)))
					new_time_arr.append(twilight_start + datetime.timedelta(seconds=float(delay)))
				else:
					time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(delay)))
					new_time_arr.append(datetime.datetime.strptime(str(time_arr[-1]), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=float(delay)))
				break
			else:
				point_inserted = 0

		try:
			plt.plot_date(new_time_arr[1:], new_star_alt_arr[1:], '-b*')
			plt.plot_date(new_time_arr[1:], numpy.ones((len(new_time_arr[1:]))), '-k', linewidth=3)
		except Exception,e:
			print e

		try:
			if new_star_alt_arr[1] > 0:

				if obs_mode.lower() == "iodine":
					mode_to_plot = "i2"
				elif obs_mode.lower() == "none-iodine":
					mode_to_plot = "ThAr"
				elif obs_mode.lower() == "template":
					mode_to_plot = "Template"

				if object_name + " " + mode_to_plot not in objects:

					plt.text(new_time_arr[int(numpy.floor(len(new_time_arr) / 2.))], new_star_alt_arr[int(numpy.floor(len(new_time_arr) / 2.))], obj_number,weight="bold", size=12, horizontalalignment='right', verticalalignment='bottom')
					objects.append(object_name + " " + mode_to_plot)
					obj_list.append(str(obj_number) + ": " +object_name + " " + mode_to_plot)
					obj_number += 1
				else:
					ii = 1
					for o in objects:
						if object_name + " " + mode_to_plot == o:
							obj_number2 = ii
						ii+=1
					plt.text(new_time_arr[int(numpy.floor(len(new_time_arr) / 2.))], new_star_alt_arr[int(numpy.floor(len(new_time_arr) / 2.))], obj_number2, weight="bold", size=12, horizontalalignment='right', verticalalignment='bottom')					
		except Exception,e:
			print e
			print "Could not append some coordinate thing"
					
		i += 1
		if i == 3000:
			print "number of max iterations reached"
			break

	print "Creating the Moon plot"
	try:
		number_of_points_in_plot = 100
		for i in range(number_of_points_in_plot):
			time_step = start_time + ((stop_time - start_time) / number_of_points_in_plot) * i

			moon_alt_val = moon_alt(time_step)
			moon_altitude = float(str(moon_alt_val).split(":")[0]) + float(str(moon_alt_val).split(":")[1]) / 60. + float(str(moon_alt_val).split(":")[2]) / 3600.

			moon_alt_arr.append(moon_altitude)
			time_arr2.append(time_step)
	except Exception,e:
		print e
		print "Could not draw second moon thing"	

#	try:
#		plt.plot_date(time_arr, star_alt_arr, 'b*')
#	except Exception,e:
#		print e
	try:
		plt.plot_date([twilight_start, twilight_start], [0,90], 'g--', linewidth=2)
	except Exception,e:
		print e
	try:
		plt.plot_date([twilight_stop, twilight_stop], [0,90], 'g--', linewidth=2)
	except Exception,e:
		print e
	try:
		plt.plot_date(time_arr2, moon_alt_arr, 'c--', linewidth=1)
	except Exception,e:
		print e
	try:
		plt.plot_date([start_time, stop_time], [m_conf.telescope_min_altitude,m_conf.telescope_min_altitude], 'r--', linewidth=2)
	except Exception,e:
		print e

	try:
		index = numpy.where(numpy.logical_and((numpy.array(moon_alt_arr) > 0.0), (numpy.array(moon_alt_arr) < 20.0)))[0]
		moon_label_index = len(index) / 2
	except Exception,e:
		print e
		print "Could not draw second moon thing"		

	try:
		plt.text(time_arr2[index[len(index)-1] - len(index) / 2], moon_alt_arr[index[len(index)-1] - len(index) / 2], "Moon", size=10, horizontalalignment='center', verticalalignment='center')
	except Exception,e:
		print e
		print "The moon was not up today"

	try:
		plt.text(time_arr2[len(time_arr2) / 2], 3, "Used time", size=10, horizontalalignment='center', verticalalignment='center')
	except Exception,e:
		print e

	plt.text(twilight_start, 92, "Nau. Twilight begins", size=10, horizontalalignment='center', verticalalignment='center')
	plt.text(twilight_stop, 92, "Nau. Twilight ends", size=10, horizontalalignment='center', verticalalignment='center')
	plt.text(time_arr2[len(time_arr2) / 2],14, "SONG telescope lower limit", size=8, horizontalalignment='center', verticalalignment='center')


	plt.grid()
	plt.ylim([0,90])
	plt.xlim([start_time,stop_time])
	plt.xlabel("UTC Hours", size=10)
	plt.ylabel("Altitude", size=10)

	plt.title("Theoretical plot for the night: %s" % (str(start_time).split(" ")[0]), size=10)

	plt.figtext(0.82, 0.77, "Targets:", size=12, fontweight='bold', verticalalignment='top')

	if len(objects) == 0 and len(obj_list) == 0:
		obj_list = ["None"]
	
	print "Lenght of night: %.2f hours" % float(len_night)
	print "Used hours of the night: %0.2f hours" % (numpy.sum(numpy.array(exp_times)) / 3600.)

	try:
		len_night_str = "%.2f" % float(len_night)
		plt.figtext(0.82, 0.92, "Lenght of night:" , size=8, verticalalignment='top')
#		plt.figtext(0.82, 0.90, "%s hours" % len_night_str, size=8, verticalalignment='top')

		total_readout_seconds = float(len_night_str) * 3600.
		ro_h = int(numpy.floor(total_readout_seconds / 3600.))
		ro_m = int(numpy.floor(((total_readout_seconds / 3600.) - ro_h ) * 60.))
		ro_s = int(numpy.floor(((((total_readout_seconds / 3600.) - ro_h ) * 60.) - ro_m ) * 60.))
		plt.figtext(0.82, 0.90, "%02d:%02d:%02d" % (ro_h, ro_m, ro_s), size=8, verticalalignment='top')

	except Exception,e:
		print "Could not add lenght of night time"

	try:
		plt.figtext(0.82, 0.87, "Integration time:" , size=8, verticalalignment='top')
#		plt.figtext(0.82, 0.85, "%0.2f hours" % (numpy.sum(numpy.array(exp_times)) / 3600.), size=8, verticalalignment='top')

		total_readout_seconds = numpy.sum(numpy.array(exp_times))
		ro_h = int(numpy.floor(total_readout_seconds / 3600.))
		ro_m = int(numpy.floor(((total_readout_seconds / 3600.) - ro_h ) * 60.))
		ro_s = int(numpy.floor(((((total_readout_seconds / 3600.) - ro_h ) * 60.) - ro_m ) * 60.))
		plt.figtext(0.82, 0.85, "%02d:%02d:%02d" % (ro_h, ro_m, ro_s), size=8, verticalalignment='top')

	except Exception,e:
		print "Could not add lenght of night time"

	try:
		plt.figtext(0.82, 0.82, "Read out time:" , size=8, verticalalignment='top')
		total_readout_seconds = len(numpy.array(time_arr)) * 2.1
		ro_h = int(numpy.floor(total_readout_seconds / 3600.))
		ro_m = int(numpy.floor(((total_readout_seconds / 3600.) - ro_h ) * 60.))
		ro_s = int(numpy.floor(((((total_readout_seconds / 3600.) - ro_h ) * 60.) - ro_m ) * 60.))
		plt.figtext(0.82, 0.80, "%02d:%02d:%02d" % (ro_h, ro_m, ro_s), size=8, verticalalignment='top')
	except Exception,e:
		print "Could not add lenght of night time"


	line_split = 0.72	
	for obj in obj_list:
		plt.figtext(0.82, line_split, str(obj.strip()), size=10)
		line_split = line_split - 0.03

#	yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
#	folder_date = yesterday.strftime('%Y%m%d')

#	plt.savefig("/scratch/star_spec/"+folder_date+"/night_"+folder_date+".png")
	try:
		if db_data == 1:	
			plt.savefig("/var/www/new_web_site/images/theory_plots/"+im_name)
		else:
			plt.savefig("/var/www/test/check_plots/check_plot_" + im_name + ".png")
	except Exception,e:
		print "Could not add lenght of night time"
		plt.savefig("/scratch/theory_plot.jpg")
#	return "/scratch/star_spec/"+folder_date+"/night_"+folder_date+".png"
	return 1

