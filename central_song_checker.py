import song_checker_config
import numpy
import psycopg2
import song_star_checker
import decimal
import numpy
import song_timeclass
import time
import datetime
import imp
import master_config as m_conf
import sys
import gc

clock = song_timeclass.TimeClass()

site_param = m_conf.song_site

class Checker(object):
   """
      @brief: This class will return good or bad values for weather, star position, sun position etc. when called. 

      @author: Mads Fredslund Andersen.

      Created Apr. 2011
   """

   def get_fields(self, curr, table_name, fields=[]):
      field_str = ''
      for field in fields:
         field_str += field
         field_str += ','
      field_str = field_str[0:-1]
	
      stmt = 'SELECT %s FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s)' % (field_str, table_name, table_name)
      curr.execute(stmt)
      results = curr.fetchone()
      res_dict = {}
      for i in range(len(results)):
         res_dict[fields[i]] = results[i]
      return res_dict

   def get_fields_req_no(self, curr, table_name, fields=[], req_no=""):
      field_str = ''
      for field in fields:
         field_str += field
         field_str += ','
      field_str = field_str[0:-1]
	
      stmt = 'SELECT %s FROM %s WHERE req_no = %s' % (field_str, table_name, req_no)
      curr.execute(stmt)
      results = curr.fetchone()
      res_dict = {}
      for i in range(len(results)):
         res_dict[fields[i]] = results[i]
      return res_dict

   def get_fields_time_int(self, curr, table_name, fields=[], time_int=0):
      field_str = ''
      for field in fields:
         field_str += field
         field_str += ','
      field_str = field_str[0:-1]

	
      stmt = "SELECT %s FROM %s WHERE ins_at > current_timestamp - INTERVAL '%s minutes'" % (field_str, table_name, str(time_int))
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

   def collect_data_from_db(self, table):
      """
         @breif: This function will return all entries from the given table in the database with the newest timestamp.
      """
      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         curr.execute("SELECT * FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s)" % (table, table))
         #output = curr.fetchall()
         output = curr.fetchone()
         curr.close()
         conn.close()
         return output
      except Exception, e:
        print clock.timename(), " Error: ", e
        return 0

   def collect_specific_data_db(self, value, table, time_int):
      """
         @breif: This function will return all entries from the given table in the database with the newest timestamp.
      """
      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         curr.execute("SELECT %s, ins_at FROM %s WHERE ins_at > current_timestamp - INTERVAL '%s minutes')" % (value, table, str(time_int)))
         output_specific = curr.fetchall()
         #output = curr.fetchone()
         curr.close()
         conn.close()
         return output_specific
      except Exception, e:
        print clock.timename(), " Error: ", e
        return 0

   def weather_check(self, deduced=0):
      """
         @breif: This function will return a value which corresponds to the weather conditions at the given time. 
      """
      imp.reload(song_checker_config)

      weather_value = 0

      sun_handle = song_star_checker.sun_pos(site=m_conf.song_site) # site=1: Tenerife

      tmp_time_str2 = datetime.datetime.strptime(str(song_star_checker.sun_pos(site=m_conf.song_site).sun_set_next()), "%Y/%m/%d %H:%M:%S")
      time_diff = tmp_time_str2-datetime.datetime.utcnow()
      hours_to_next_sun_set = int(time_diff.days) * 24. + time_diff.seconds / (24.*3600.) * 24		# Time until next sunset in seconds

      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         weather_output = self.get_fields(curr, "weather_station", ["ins_at", "wxt520_temp1", "wxt520_humidity", "wxt520_pressure", "wxt520_rain_int", "drd11_rain", "wxt520_wind_speed", "wxt520_wind_direction", "wxt520_wind_avg", "wxt520_wind_avgdir", "bw_cloud_cond", "bw_rain_cond", "bw_sky_cond", "bw_wind_cond", "bw_delta_temp", "bw_temp_amb", "bw_windspeed", "bw_wetsensor", "bw_rainsensor", "bw_humidity", "bw_dewp_temp", "bw_temp_case", "bw_day_cond", "bw_day_inten", "dust_level"])
         time_diff = datetime.datetime.utcnow()-weather_output["ins_at"]
         time_diff = time_diff.days*24*3600 + time_diff.seconds
      except Exception, e:
        print clock.timename(), " Error: ", e

      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         rain_output = self.get_fields_time_int(curr, "weather_station", ["drd11_rain", "wxt520_rain_int", "bw_rain_cond","bw_cloud_cond"], song_checker_config.search_time)
      except Exception, e:
        print clock.timename(), " Error: ", e

      drd11_rain_arr = rain_output["drd11_rain"]
      wxt520_rain_arr = rain_output["wxt520_rain_int"]
      boltwood_rain_arr = rain_output["bw_rain_cond"]
      boltwood_cloud_arr = rain_output["bw_cloud_cond"]

      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         output_dome = self.get_fields(curr, "tel_dome", ["tel_az", "dome_az", "ins_at"])
      except Exception, e:
        print clock.timename(), " Could not get the telescope values for dome and telescope azimuth"
      
      try:
         dome_azimuth = output_dome["dome_azimuth"]
      except Exception,e:
         dome_azimuth = 1 # If no output_dome

      if float(weather_output["wxt520_temp1"]) >= song_checker_config.max_temp or float(weather_output["wxt520_temp1"]) <= song_checker_config.min_temp: # Temperature from WXT520
         weather_value = weather_value + 1
      if float(weather_output["wxt520_humidity"]) >= song_checker_config.max_hum: # Humidity from WXT520.
         weather_value = weather_value + 2
      if float(weather_output["wxt520_wind_avg"]) >= song_checker_config.max_w_speed:# Wind speed from WXT520.
         weather_value = weather_value + 4

	##### I am using the telescope azimuth in stead of dome azimuth since I am not sure this only goes from 0 to 360. #### 
      if float(weather_output["wxt520_wind_avg"]) >= song_checker_config.max_w_speed_into and (numpy.abs(float(output_dome['tel_az']) - float(weather_output["wxt520_wind_avgdir"])) <= song_checker_config.angle_into or numpy.abs(float(output_dome['tel_az']) - float(weather_output["wxt520_wind_avgdir"])) >= (360.0 - song_checker_config.angle_into)): # Wind into the dome.
         print clock.timename(), "The wind speed into the dome was too high. Wind dir = %s, Telescope az = %s" % (str(float(weather_output["wxt520_wind_avg"])), str(float(output_dome['tel_az']))) 
         weather_value = weather_value + 8  

	# Boltwood cloud detector, 0 = unknown, 1 = clear, 2 = cloudy, 3 = very cloudy.
      cloud_events = 0	
      for i in song_checker_config.clouds:
		cloud_events = cloud_events + len(numpy.where(numpy.array(boltwood_cloud_arr) == i)[0])
		if cloud_events > song_checker_config.max_rain_events:
			if weather_value < 16:			
				weather_value = weather_value + 16

      #if cloud_events > song_checker_config.max_rain_events:
         #print "Number of cloud events: ", cloud_events

	################## IF ALL THREE RAIN DETECTORS DETECT RAIN AT THE SAME TIME I EXPECT IT TO BE TRUE ##########
      if int(weather_output["drd11_rain"]) != 0 and float(weather_output["wxt520_rain_int"]) > 0 and int(weather_output["bw_rain_cond"]) != 1 and len(song_checker_config.rain_detector) == 3: # All three rain detectors detects rain.
         weather_value = weather_value + 32
	 #print "All three rain detectors triggerd"
	##### IF TWO RAIN DETECTORS TRIGGERS AT THE SAME TIME I EXPECT IT TO BE TRUE ########## 
      elif (int(weather_output["drd11_rain"]) != 0 and float(weather_output["wxt520_rain_int"]) > 0) or (int(weather_output["bw_rain_cond"]) != 1 and float(weather_output["wxt520_rain_int"]) > 0) or (int(weather_output["bw_rain_cond"]) != 1 and int(weather_output["drd11_rain"]) != 0) and len(song_checker_config.rain_detector) == 2:
         weather_value = weather_value + 32 # two of the three detectors detects rain.
	 #print "Two rain detectors triggerd"
	###### IF ONLY ONE TRIGGERS IT WILL CHECK IF MORE THAN ONE EVENT OCCURED ######
      elif int(weather_output["drd11_rain"]) != 0 or float(weather_output["wxt520_rain_int"]) > 0 or int(weather_output["bw_rain_cond"]) != 1:
	 rain_event = 0
	 if "drd11" in song_checker_config.rain_detector:
		if len(numpy.nonzero(drd11_rain_arr)[0]) > song_checker_config.max_rain_events:
			#print "DRD11 triggered with %s rain events" % len(numpy.nonzero(drd11_rain_arr)[0])	
			weather_value = weather_value + 32
			rain_event = 1
         if "bw" in song_checker_config.rain_detector and rain_event == 0:
		if len(numpy.where(numpy.array(boltwood_rain_arr)[0] != 1)) > song_checker_config.max_rain_events:
			#print "Boltwood triggered with %s rain events" % len(numpy.where(numpy.array(boltwood_rain_arr) != 1)[0])
			weather_value = weather_value + 32
			rain_event = 1
	 if "wxt520" in song_checker_config.rain_detector and rain_event == 0:
		if len(numpy.nonzero(wxt520_rain_arr)[0]) > song_checker_config.max_rain_events:
			#print "WXT520 triggered with %s rain events" % len(numpy.nonzero(wxt520_rain_arr)[0])
			weather_value = weather_value + 32

#### Det gamle check:
#	 if len(numpy.nonzero(drd11_rain_arr)[0]) > song_checker_config.max_rain_events or len(numpy.nonzero(wxt520_rain_arr)[0]) > song_checker_config.max_rain_events or len(numpy.where(numpy.array(boltwood_rain_arr) != 1)) > song_checker_config.max_rain_events: # Rain in the last defined period. 
#           weather_value = weather_value + 32

      sun_alt_str = str(song_star_checker.sun_pos().sun_alt())

      if sun_alt_str[0] == '-':
		sun_alt = float(sun_alt_str.split(':')[0]) - float(sun_alt_str.split(':')[1]) / 60.0 - float(sun_alt_str.split(':')[2]) / 3600.0
      elif sun_alt_str[0] != '-':
		sun_alt = float(sun_alt_str.split(':')[0]) + float(sun_alt_str.split(':')[1]) / 60.0 + float(sun_alt_str.split(':')[2]) / 3600.0

      if time_diff > song_checker_config.downtime: # If insertion to database has stoped.
         weather_value = weather_value + 64
      if float(weather_output["dust_level"]) > song_checker_config.dust_limit: # Should check array for more than one event...
         weather_value = weather_value + 128
      elif float(weather_output["dust_level"]) > song_checker_config.dust_limit_daytime and sun_alt > 0.1 and hours_to_next_sun_set >= (song_checker_config.open_time_if_dust + (song_checker_config.telescope_delay_time / 60.) + 0.1):	
         weather_value = weather_value + 128


      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         wind_output = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "wxt520_wind_speed"], 15)
      except Exception, e:
         print clock.timename(), " Error: ", e
      else:
         curr.close()
         conn.close()

      wind_avg_arr = numpy.array(wind_output["wxt520_wind_avg"], dtype=numpy.float)
      wind_speed_arr = numpy.array(wind_output["wxt520_wind_speed"], dtype=numpy.float)

      if round(float(numpy.mean(wind_avg_arr)),3) == round(float(wind_avg_arr[0]),3) and round(float(numpy.mean(wind_avg_arr)),3) == round(float(wind_avg_arr[-1]),3) and round(float(numpy.mean(wind_speed_arr)),3) == round(float(wind_speed_arr[0]),3) and round(float(numpy.mean(wind_speed_arr)),3) == round(float(wind_speed_arr[-1]),3) and float(weather_output["wxt520_temp1"]) <= 2.0:
#		print clock.timename(), " The wind sensor was frozen!"
		weather_value = weather_value + 256

      if deduced == 0:
         return weather_value, weather_output["ins_at"]
      elif deduced == 1:
         if weather_value != 0:
            n_array = []
            for i in (2**9,2**8,2**7,2**6,2**5,2**4,2**3,2**2,2**1,2**0):
               if weather_value >= i:
                  n_array.append(i)
                  weather_value -= i
         else:
            n_array = [0]

         return n_array, weather_output["ins_at"]

   def day_check(self, site=site_param):
      """
         @brief: This function will determine whether it is day, night or twilight. 
      """
      imp.reload(song_checker_config)

      day_value = 0

      sun_alt_str = str(song_star_checker.sun_pos(site=m_conf.song_site).sun_alt())

      if sun_alt_str[0] == '-':
		sun_alt = float(sun_alt_str.split(':')[0]) - float(sun_alt_str.split(':')[1]) / 60.0 - float(sun_alt_str.split(':')[2]) / 3600.0
      elif sun_alt_str[0] != '-':
		sun_alt = float(sun_alt_str.split(':')[0]) + float(sun_alt_str.split(':')[1]) / 60.0 + float(sun_alt_str.split(':')[2]) / 3600.0

      #print "Altitude of the Sun is: %f at %s" % (sun_alt, clock.obstimeUT())

      if sun_alt < -18.0: # Night
         day_value = -1               

      if sun_alt >= -18.0 and sun_alt < -12.0: # Astronomical twilight
         day_value = 1

      if sun_alt >= -12.0 and sun_alt < -6.0: # Nautical twilight
         day_value = 2
      
      if sun_alt >= -6.0 and sun_alt < -0.5: # Civil twilight
         day_value = 3
 
      if sun_alt >= -0.5: # Day
         day_value = 4

      return day_value

   def object_check(self, object_ra, object_dec, site=site_param):
	"""
		@brief: This function will determine whether or not an object is observable at the moment. 
	"""
	object_value = 0

	if float(str(song_star_checker.star_pos(site).star_alt(object_ra, object_dec)).split(':')[0]) < m_conf.telescope_min_altitude: 
		object_value = 1    
	elif float(str(song_star_checker.star_pos(site).star_alt(object_ra, object_dec)).split(':')[0]) >= m_conf.max_alt_auto: 
		object_value = 4    


      	#### Check if wind is too high coming from the stars position:
	object_az = song_star_checker.star_pos(site=1).star_az(star_ra=object_ra, star_dec=object_dec)
	object_az = float(str(object_az).split(":")[0])
	
	test = False
	if test == False:
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			wind_data = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "wxt520_wind_speed", "wxt520_wind_avgdir", "ins_at"], 20)	# search for high wind speeds in last 20 minutes
		except Exception, e:
			print clock.timename(), " Error: ", e		
		else:
			curr.close()
			conn.close()
	#	print wind_data["wxt520_wind_avg"]

	#	print len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_w_speed_into)[0])
	#	print numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_w_speed_into)[0]
	#	print float(wind_data["wxt520_wind_avgdir"][-1])
	#	print object_az
	#	print numpy.abs(object_az - float(wind_data["wxt520_wind_avgdir"][-1]))

	   
		if len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_w_speed_into)[0]) >= song_checker_config.wind_blow_events and (numpy.abs(object_az - float(wind_data["wxt520_wind_avgdir"][-1])) <= (song_checker_config.angle_into + song_checker_config.insert_margin) or numpy.abs(object_az - float(wind_data["wxt520_wind_avgdir"][-1])) >= (360.0 - song_checker_config.angle_into - song_checker_config.insert_margin)):
			object_value = object_value + 2 

	del wind_data
	  
	return object_value

   def object_check2(self, object_ra, object_dec, high_wind, last_wind_dir, site=site_param):
	"""
		@brief: This function will determine whether or not an object is observable at the moment. 
	"""
	object_value = 0
	
	if float(str(song_star_checker.star_pos(site).star_alt(object_ra, object_dec)).split(':')[0]) < m_conf.telescope_min_altitude: 
		object_value = 1    
	elif float(str(song_star_checker.star_pos(site).star_alt(object_ra, object_dec)).split(':')[0]) >= m_conf.max_alt_auto: 
		object_value = 4    

      	#### Check if wind is too high coming from the star position:
	object_az = song_star_checker.star_pos(site=1).star_az(star_ra=object_ra, star_dec=object_dec)
	object_az = float(str(object_az).split(":")[0])	

	if high_wind == 1 and (numpy.abs(object_az - float(last_wind_dir)) <= (song_checker_config.angle_into + song_checker_config.insert_margin) or numpy.abs(object_az - float(last_wind_dir)) >= (360.0 - song_checker_config.angle_into - song_checker_config.insert_margin)):
		object_value = object_value + 2 

	  
	return object_value

   def seeing_check(self, vmag, slit, alt):
	"""
		@brief: If we are observing faint objects the seeing should be good. 
		This function will return 0 if seeing is below limit and seeing data is up to date. Otherwise it will return 1.
	"""

	search_interval = 20	

	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		curr.execute("SELECT extra_param_1, ins_at FROM tenerife_tel_temps WHERE ins_at > current_timestamp - INTERVAL '%s minutes' AND extra_param_1 > 0" % (str(search_interval)))
		seeing_data = curr.fetchall()
		curr.close()
		conn.close()
	except Exception, e:
		print clock.timename(), "Error: ", e
		return 1
	
	else:		
		time_arr = []
		seeing_arr = []
		for line in seeing_data:
			time_arr.append(line[1])
			seeing_arr.append(float(line[0]))

	# first check time of data:
	if len(time_arr) > 0:
		t_diff = time_arr[0] - (datetime.datetime.utcnow() - datetime.timedelta(minutes=search_interval))
		
		alt_factor = (116 - alt) / 100.

		if t_diff.seconds > 600:	
			print clock.timename(),"Seeing data was not up to date"
			return 1
	#	else:
	#		print clock.timename(), "Seeing data ready..."
		median_seeing = numpy.median(numpy.array(seeing_arr)) * alt_factor
		print clock.timename(), " The median seeing value times the altitude factor was: ", median_seeing

		if slit == 5 and median_seeing > m_conf.seeing_limit_s5:
			print clock.timename(), "The seeing was not good"
			return 2
		elif slit == 6 and median_seeing > m_conf.seeing_limit_s6:
			print clock.timename(), "The seeing was not good"
			return 2
		elif slit == 8 and median_seeing > m_conf.seeing_limit_s8:
			print clock.timename(), "The seeing was not good"
			return 2
		else:
			print clock.timename(), "The seeing was good..."
			return 0
			
	else:
		return 3
	
		

   def wind_check(self):
      """
         @brief: This function will determine whether or not an object is observable at the moment. 
      """
      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         wind_data = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "wxt520_wind_avgdir", "ins_at"], song_checker_config.search_time)
      except Exception, e:
         print clock.timename(), " Error: ", e
      else:
         curr.close()
         conn.close()
      #print "Wind speed: %.1f, wind direction: %.1f, Inserted at: %s"  % (wind_data["wxt520_wind_avg"][len(wind_data["wxt520_wind_avg"])-1], wind_data["wxt520_wind_avgdir"][len(wind_data["wxt520_wind_avgdir"])-1], wind_data["ins_at"][len(wind_data["ins_at"])-1])
      return_value = []

      if len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_wind_side_ports)[0]) >= song_checker_config.wind_blow_events: # Wind into side ports.
         if numpy.abs(float(wind_data["wxt520_wind_avgdir"][-1]) - 358.0) <= song_checker_config.side_ports_angle or float(wind_data["wxt520_wind_avgdir"][-1]) <= song_checker_config.side_ports_angle - 2.0:
	    return_value.append(3) # If wind direction is from "North".
         if numpy.abs(float(wind_data["wxt520_wind_avgdir"][-1]) - 101.0) <= song_checker_config.side_ports_angle:
	    return_value.append(4) # If wind direction is from "East".
         if numpy.abs(float(wind_data["wxt520_wind_avgdir"][-1]) - 177.0) <= song_checker_config.side_ports_angle:
	    return_value.append(1) # If wind direction is from "South".
         if numpy.abs(float(wind_data["wxt520_wind_avgdir"][-1]) - 254.0) <= song_checker_config.side_ports_angle:
	    return_value.append(2) # If wind direction is from "West".

      return return_value

   def wind_check_dome_flap(self):
      """
         @brief: This function will determine whether or not an object is observable at the moment. 
      """
      imp.reload(song_checker_config)
      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         wind_data = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "ins_at"], song_checker_config.search_time)
      except Exception, e:
        print clock.timename(), " Error: ", e
      else:
         curr.close()
         conn.close()
	
      if len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_w_speed_flap)[0]) >= song_checker_config.wind_blow_events: # Wind into side ports.
		allow_to_open = 0
      else:
		allow_to_open = 1

      return allow_to_open

   def low_wind_speed(self):
	"""
		@brief: This function will determine whether or not an object is observable at the moment. 
	"""
	imp.reload(song_checker_config)
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		wind_data = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "wxt520_wind_avgdir", "ins_at"], (song_checker_config.day_search_time))	# Checks last 40 minutes.
	except Exception, e:
		print clock.timename(), " Error: ", e

	if len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_wind_side_ports)[0]) >= song_checker_config.wind_blow_events: # Wind speed too high into side ports.
		return 1
	elif numpy.mean(numpy.array(wind_data["wxt520_wind_avg"],dtype=float)) <= song_checker_config.min_wind_side_ports: # Wind speed too low into side ports.
		return 2
	else:
		return 0	

   def rain_and_hum(self):
      """
         @brief: This checks the rain and humidity status for use to control side ports.
      """
      imp.reload(song_checker_config)
      try:
         conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
         curr = conn.cursor()
         rain_and_hun_output = self.get_fields_time_int(curr, "weather_station", ["drd11_rain", "wxt520_rain_int", "bw_rain_cond", "wxt520_humidity"], song_checker_config.search_time)
      except Exception, e:
        print clock.timename(), " Error: ", e
      else:
         curr.close()
         conn.close()

      drd11_rain_arr = rain_and_hun_output["drd11_rain"]
      wxt520_rain_arr = rain_and_hun_output["wxt520_rain_int"]
      boltwood_rain_arr = rain_and_hun_output["bw_rain_cond"]
      wxt520_humidity_arr = rain_and_hun_output["wxt520_humidity"]

      #print "Rain events: ", len(numpy.where(numpy.array(drd11_rain_arr) == 1)[0]), len(numpy.where(numpy.array(wxt520_rain_arr) > 0)[0]), len(numpy.where(numpy.array(boltwood_rain_arr) != 1)[0]), "Humidity: ", wxt520_humidity_arr[len(wxt520_humidity_arr)-1]

      if len(numpy.where(numpy.array(drd11_rain_arr) == 1)[0]) > song_checker_config.side_port_events or len(numpy.where(numpy.array(wxt520_rain_arr) > 0)[0]) > song_checker_config.side_port_events or len(numpy.where(numpy.array(boltwood_rain_arr) != 1)[0]) > song_checker_config.side_port_events or float(wxt520_humidity_arr[len(wxt520_humidity_arr)-1]) > float(song_checker_config.max_hum):
         return 1 # Should trigger all side ports to close.
      else:
         return 0 # Should do nothing

   def open_time(self,site=site_param):
      """
         @brief: This will return a value about opening time at the begining of every night.
      """
      imp.reload(song_checker_config)
      time_value = 0

      if song_star_checker.sun_pos(site).sun_set_next() < m_conf.side_port_open_time: 
         time_value = 1               

      return time_value


   def check_obs_state(self):
	"""
		@brief: This will return a value about the over all observation state.
		Returns 0 if everything is okay and a number from 1 to 6 if not.
	"""
        imp.reload(song_checker_config)
	weather_val = self.weather_check(deduced=0)	
	if str(weather_val[0]) != '0':
		#print "Weather value was: ", weather_val[0]
		return 1 		

	day_val = self.day_check(site=site_param)
	if str(day_val) == '4':
		#print "Day value was: ", day_val
		return 2 

	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		tel_dome_output = self.get_fields(curr, "tel_dome", ["tel_alt","tel_motion_state", "dome_slit_state", "mirror_cover_state", "ins_at"])
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 3
        else:
		curr.close()
		conn.close()
	motion_state = tel_dome_output["tel_motion_state"]
	slit_state = tel_dome_output["dome_slit_state"]
	mirror_cover_state = tel_dome_output["mirror_cover_state"]
	timestamp = tel_dome_output["ins_at"]

	if str(slit_state) not in ['1', '1.0']:
		#print clock.timename(), " Dome slit state was: %s, at: %s" % (str(slit_state), clock.obstimeUT())
		return 5

	if str(mirror_cover_state) not in ['1', '1.0']:
		#print clock.timename(), " Telescope mirror cover state was: %s, at: %s" % (str(mirror_cover_state), clock.obstimeUT())
		return 6

	if str(motion_state) not in ['11', '11.0', '1', '1.0']:
		if float(tel_dome_output["tel_alt"]) <= float(m_conf.telescope_min_altitude):
			return 7
		else:
			return 4

	if datetime.datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S") < (datetime.datetime.utcnow() - datetime.timedelta(seconds=300)):
		return 8

	return 0


   def check_for_or_start(self):
	"""
		@brief: This will return a value about the observing state.
		Returns 0 if everything is okay and a number from 1 to 6 if not.
	"""
        imp.reload(song_checker_config)

	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		tel_dome_output = self.get_fields(curr, "tel_dome", ["tel_motion_state", "dome_slit_state", "ins_at", "extra_param_2"])
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 1
 	else:
		curr.close()
		conn.close()
	motion_state = tel_dome_output["tel_motion_state"]
	slit_state = tel_dome_output["dome_slit_state"]
	tel_state = tel_dome_output["extra_param_2"]

	if str(slit_state) not in ['1', '1.0']:
#		return 2
		return "[Dome not open]"

	if str(motion_state) in ['11', '11.0']:
#		return 3
		return "[Telescope still tracking]"

	if datetime.datetime.strptime(str(tel_dome_output["ins_at"]), "%Y-%m-%d %H:%M:%S") < (datetime.datetime.utcnow() - datetime.timedelta(seconds=300)):
#		return 4
		return "[Time stamp too old]"

	if float(tel_state) == 1.0:
#		return 5
		return "[Telescope starting up]"

	elif float(tel_state) == 2.0:
#		return 6
		return "[Telescope shutting down]"

	return 0


   def wind_check_test(self):
      imp.reload(song_checker_config)
      return_value = []

      wind_speed = numpy.random.random()*15
      wind_dir = numpy.random.random()*360

      print ""
      print song_timeclass.TimeClass().whattime()
      print "Wind speed: %.1f" % wind_speed
      print "Wind direction: %.1f" % wind_dir
   
      if wind_speed > song_checker_config.max_windde_ports:
         if numpy.abs(wind_dir - 358.0) <= song_checker_config.side_ports_angle or wind_dir <= song_checker_config.side_ports_angle - 2.0:
	    return_value.append(3) # If wind direction is from "North".
         if numpy.abs(wind_dir - 101.0) <= song_checker_config.side_ports_angle:
	    return_value.append(4) # If wind direction is from "East".
         if numpy.abs(wind_dir - 177.0) <= song_checker_config.side_ports_angle - 30.0:
	    return_value.append(1) # If wind direction is from "South".
         if numpy.abs(wind_dir - 254.0) <= song_checker_config.side_ports_angle:
	    return_value.append(2) # If wind direction is from "West".

      return return_value

   def weather_check_test(self):
      return int(round(numpy.random.random()*0.52)), ""

   def rain_and_hum_test(self):
      return int(round(numpy.random.random()*0.51))

   def check_slony(self):
	"""
		@brief: If return value is 0 everything is fine. If return value is 1 replication of ORs from central to tenerife is down. If value is 2 replication of data from tenerife to central is down. If value is 3 all replication is down. If value is 4 connection to local database is gone. If value is 5 connection to central database is gone. 
	"""
	
#####################################################################################
	#### Get the OR with the hights request number from tenerife
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		or_tenerife_output = self.get_fields(curr, "obs_request_1", ["req_no","ins_at"])
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 4
	else:
		curr.close()
		conn.close()

	req_no_tenerife = or_tenerife_output["req_no"]
	ins_at_tenerife = datetime.datetime.strptime(str(or_tenerife_output["ins_at"]), "%Y-%m-%d %H:%M:%S")

	#### Get the OR with the hights request number from central
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		or_central_output = self.get_fields(curr, "obs_request_1", ["req_no","ins_at"])
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 5
	else:
		curr.close()
		conn.close()
	req_no_central = or_central_output["req_no"]
	ins_at_central = datetime.datetime.strptime(str(or_central_output["ins_at"]), "%Y-%m-%d %H:%M:%S")

#####################################################################################
	#### Get weather data with the hights insert time stamp from central
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		weather_central_output = self.get_fields(curr, "weather_station", ["ins_at", "weather_station_id"])
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 5
	else:
		curr.close()
		conn.close()
	weather_id_central = weather_central_output["weather_station_id"]
	weather_ins_at_central = weather_central_output["ins_at"]

	weather_tenerife_output = [0]
	#### Check if weather data with timestamp from central exists on Tenerife
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		weather_tenerife_output = self.get_fields(curr, "weather_station", ["ins_at", "weather_station_id"])
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 4
	else:
		curr.close()
		conn.close()
	weather_id_tenerife = weather_tenerife_output["weather_station_id"]
	weather_ins_at_tenerife = weather_tenerife_output["ins_at"]
#####################################################################################

	return_value = 0
	if req_no_central != req_no_tenerife and ins_at_central < (datetime.datetime.utcnow() - datetime.timedelta(seconds=600)):
		return_value = 1
	if weather_id_tenerife != weather_id_central and weather_ins_at_central < (datetime.datetime.utcnow() - datetime.timedelta(seconds=600)):
		return_value = return_value + 2

	return return_value

   def check_for_ors(self):
	# Search for an OR that will start within the first 2 hours after sunset.
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		curr.execute("SELECT req_no FROM obs_request_1 WHERE start_window < (now() + INTERVAL '1 hours') and stop_window > now()")
		output_or = curr.fetchall()
		curr.close()
		conn.close()
	except Exception, e:
		print clock.timename(), " Error: ", e
		return 0

	def check_or_status(request_number):
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			curr.execute("SELECT status FROM obs_request_status_1 WHERE req_no=%s" % (request_number))
			output_or = curr.fetchone()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e
			return "abort"
	
		return output_or

	numb_of_ors = 0
	try:
		for line in output_or:
			or_state = check_or_status(line[0])
			if or_state[0] == "wait":
				print clock.timename(), "OR with number: '%s' and status: '%s' is pending" % (str(line[0]), str(or_state[0]))
				numb_of_ors +=1
	except Exception,e:
		print clock.timename(), " Error: ", e
		numb_of_ors = 0
	
	if numb_of_ors == 0:
		return 0
	else:
		return 1


   def check_o_star(self, o_star_name, site=site_param):
	
	"""
		@brief: This function will determine whether or not an object is observable at the moment. 
	"""

	sys.path.append(song_checker_config.o_star_dir) 
	o_star_filename = o_star_name + "_o-star.py"

	try:
		template_config = __import__(str(o_star_filename ).split('.')[0])
	except Exception, e:
		print e
		return 4

	object_value = 0

	if float(str(song_star_checker.star_pos(site).star_alt(template_config.ostar_ra_hours, template_config.ostar_dec_degrees)).split(':')[0]) < m_conf.telescope_min_altitude: 
		object_value = 1    

      	#### Check if wind is too high coming from the stars position:
	object_az = song_star_checker.star_pos(site=1).star_az(star_ra=template_config.ostar_ra_hours, star_dec=template_config.ostar_dec_degrees)
	object_az = float(str(object_az).split(":")[0])
	
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		wind_data = self.get_fields_time_int(curr, "weather_station", ["wxt520_wind_avg", "wxt520_wind_speed", "wxt520_wind_avgdir", "ins_at"], 20)	# search for high wind speeds in last 20 minutes
	except Exception, e:
		print clock.timename(), " Error: ", e		
	else:
		curr.close()
		conn.close()

	if len(numpy.where(numpy.array(wind_data["wxt520_wind_avg"],dtype=float) >= song_checker_config.max_w_speed_into)[0]) >= song_checker_config.wind_blow_events and (numpy.abs(object_az - float(wind_data["wxt520_wind_avgdir"][-1])) <= song_checker_config.angle_into or numpy.abs(object_az - float(wind_data["wxt520_wind_avgdir"][-1])) >= (360.0 - song_checker_config.angle_into)):
		object_value = object_value + 2 
  

	return object_value







      
