"""
   Created on Apr 19, 2010

   @author: Mads Fredslund Andersen

   @todo: This module should and could be modified to take location coordinates to each calculation. So other observatories could use this module.
"""

import string
import sys
import ephem
import song_timeclass
import song_convert_coor

clock = song_timeclass.TimeClass()

# This sets the coordinates for the observatory:
epoch = 2000 #epoch for coordinate determination

def site_values(site):
   if site == 5: # Hawaii
      obs_lat = "21.32" #latitude of the observatory
      obs_lon = "157.8" #longitude of the observatory with base "west"
      obs_elev = 2000 #elevation of the observatory
   elif site == 1 or site == "tenerife": # Tenerife
      obs_lat = "28.2983" #latitude of the observatory
      obs_lon = "-16.5094" #longitude of the observatory with base "west"
      obs_elev = 2400 #elevation of the observatory
   elif site == 3: # Aarhus
      obs_lat = "56.17141" #latitude of the observatory
      obs_lon = "10.20039" #longitude of the observatory with base "west"
      obs_elev = 50 #elevation of the observatory
   elif site == 4: # La Silla
      obs_lat = "-29.261167" #latitude of the observatory
      obs_lon = "-70.731333" #longitude of the observatory with base "west"
      obs_elev = 2340 #elevation of the observatory

   return obs_lat, obs_lon, obs_elev

class coordinates(object):
   """
      @brief: This class checks coordinates on the sky.
   """
   def coordinate_check(self, star_ra, star_dec):
      """
         @brief: This function checks if the coordinates makes any sense.

         @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
         @param star_dec: The declination of a star given in the format: DD:MM:SS.
      """        
      error_value = 0
      if star_ra[0] == '-':
         print '\nerror at: ',clock.whattime()
         print 'error '+str(error_value)+': star_ra must be in the range from 0.0 to 24.0'
         error_value += 1
      else:
         star_ra_hours = star_ra.split(':')
            
         if len(star_ra_hours) == 2:
            if float(star_ra_hours[1]) >= 60.0 or float(star_ra_hours[1]) < 0.0:
               print '\nerror at: ',clock.whattime()
               print 'error '+str(error_value)+': star_ra minutes must be in the range from 0.0 to 59.99...'
               error_value += 1
               star_ra_hours = 1.0
            else:                
               star_ra_hours = [float(star_ra_hours[0])+(float(star_ra_hours[1])/60),0]
                    
         if len(star_ra_hours) == 3:
            if float(star_ra_hours[1]) >= 60.0 or float(star_ra_hours[1]) < 0.0 or float(star_ra_hours[2]) >= 60.0 or float(star_ra_hours[2]) < 0.0:
               print '\nerror at: ',clock.whattime()
               print 'error '+str(error_value)+': star_ra minutes must be in the range from 0.0 to 59.99... and seconds from 0.0 to 59.99..'
               error_value += 1
               star_ra_hours = 1.0
            else:                
               star_ra_hours = [float(star_ra_hours[0])+(float(star_ra_hours[1])/60),0]
                    
         if star_ra != None and star_ra != '':
            if float(star_ra_hours[0]) < 0.0 or float(star_ra_hours[0]) > 24.0:
               print '\nerror at: ',clock.whattime()
               print 'error '+str(error_value)+': star_ra must be in the range from 0.0 to 24.0'
               error_value += 1
            else:
               star_ra = ''
        
      star_dec_deg = star_dec.split(':')
      if len(star_dec_deg) == 2:
         if float(star_dec_deg[1]) >= 60.0 or float(star_dec_deg[1]) < 0.0:
            print '\nerror at: ',clock.whattime()
            print 'error '+str(error_value)+': star_ra minutes must be in the range from 0.0 to 59.99...'
            error_value += 1
            star_dec_deg = 1.0
         else:            
            star_dec_deg = [abs(float(star_dec_deg[0]))+(float(star_dec_deg[1])/60),0]
                    
      if len(star_dec_deg) == 3:
         if float(star_dec_deg[1]) >= 60.0 or float(star_dec_deg[1]) < 0.0 or float(star_dec_deg[2]) >= 60.0 or float(star_dec_deg[2]) < 0.0:
            print '\nerror at: ',clock.whattime()
            print 'error '+str(error_value)+': star_ra minutes must be in the range from 0.0 to 59.99... and seconds from 0.0 to 59.99..'
            error_value += 1
            star_dec_deg = 1.0
         else:                
            star_dec_deg = [abs(float(star_dec_deg[0]))+(float(star_dec_deg[1])/60), 0]
                    
      if star_dec != None and star_dec != '':
         if float(star_dec_deg[0]) < -90.0 or float(star_dec_deg[0]) > 90.0:
            print '\nerror at: ',clock.whattime()
            print 'error '+str(error_value)+': star_dec must be in the range from -90.0 to +90.0'
            error_value += 1
      else:
         star_dec = ''
        
      if error_value != 0:
         sys.exit("Wrong star coordinates. Check the numbers!!!")
      else:
         return 0
    

class star_pos():
   """
      @brief: This class will do some calculations on stellar objects. This class uses the module ephem.py.
   """
   def __init__(self, site=1):
       self.obs_lat, self.obs_lon, self.obs_elev = site_values(site)

   def star_alt(self, star_ra='', star_dec='', unit='s'):
	"""
		@brief: This function will calculate the altitude of an object with given coordinates at a given time seem from Teide.

		@param star_ra: The right ascension of a star given in the format: HH:MM:SS.
		@param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""       
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec

	star.compute(song_site)
	alt_star = star.alt
	if unit == 's':		# 's' for string	
		return alt_star 
	else:			# return float value
		return float(str(alt_star).split(":")[0]) + float(str(alt_star).split(":")[1]) / 60.  + float(str(alt_star).split(":")[2]) / 3600.

   def star_alt_at(self, star_ra='', star_dec='', time_stamp='', unit='s'):
	"""
		@brief: This function will calculate the altitude of an object with given coordinates at a given time seem from Teide.

		@param star_ra: The right ascension of a star given in the format: HH:MM:SS.
		@param star_dec: The declination of a star given in the format: DD:MM:SS.
		@param time_stamp: Time of when the altitude should be calculated in the format: YYYY-MM-DD hh:mm:ss
	"""       
	song_site = ephem.Observer()
        song_site.lat = self.obs_lat
        song_site.long = self.obs_lon
        song_site.elev = self.obs_elev
	song_site.date = time_stamp

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)
	
	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec

	star.compute(song_site)
	alt_star = star.alt
	if unit == 's':		# 's' for string	
		return alt_star 
	else:			# return float value
		return float(str(alt_star).split(":")[0]) + float(str(alt_star).split(":")[1]) / 60.  + float(str(alt_star).split(":")[2]) / 3600.

        
   def star_az(self, star_ra, star_dec):
	"""
	 @brief: This function will determine the azimuth of an object with given coordinates at a given time.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')
	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec

	star.compute(song_site)
	az_star = star.az
	return az_star

   def star_rise_pre(self, star_ra, star_dec):
	"""
	 @brief: This function calculates when the object with given coordinates was rising last time.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""          
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev


#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec

	star.compute(song_site)
	rise_star = song_site.previous_rising(star)
	return rise_star
    
   def star_rise_next(self, star_ra, star_dec):
	"""
	 @brief: This function calculates when the object with given coordinates is rising next time.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""           
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev


#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec
	star.compute(song_site)
	rise_star = song_site.next_rising(star)
	return rise_star

   def star_set_pre(self, star_ra, star_dec):
	"""
	 @brief: This function calculates when the object with given coordinates was setting last time.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	""" 
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec
	star.compute(song_site)
	set_star = song_site.previous_setting(star)
	return set_star
    
   def star_set_next(self, star_ra, star_dec):
	"""
	 @brief: This function calculates when the object with given coordinates is setting next time.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev
        

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec
	star.compute(song_site)
	set_star = song_site.next_setting(star)
	return set_star
     
class sun_pos():
   """
      @brief: This class calculates positions for the Sun.
   """ 
   def __init__(self, site=1):
       self.obs_lat, self.obs_lon, self.obs_elev = site_values(site)

   def sun_alt(self,unit='s'):
	"""
	 @brief: This function will determine the altitude of the Sun.
	"""        

	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	sun = ephem.Sun()
	sun.compute(song_site)
	if unit == 's':		# 's' for string	
		return sun.alt
	else:			# return float value
		return float(str(sun.alt).split(":")[0]) + float(str(sun.alt).split(":")[1]) / 60.  + float(str(sun.alt).split(":")[2]) / 3600.
    
   def sun_az(self):
      """
         @brief: This function will determine the azimuth of the Sun.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site) 
      return sun.az

   def sun_ra(self):
      """
         @brief: This function will determine the right ascension of the Sun.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site) 
      return sun.a_ra # Astrometric Geocentric Position related to the epoch

   def sun_dec(self):
      """
         @brief: This function will determine the right ascension of the Sun.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site) 
      return sun.a_dec # Astrometric Geocentric Position related to the epoch

   def sun_rise_pre(self):
      """
         @brief: This function will determine when the Sun was rising last time.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site)
      return song_site.previous_rising(sun)
    
   def sun_rise_next(self):
      """
         @brief: This function will determine when the Sun is rising next time.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site)
      return song_site.next_rising(sun)
    
   def sun_set_pre(self):
      """
         @brief: This function will determine when the Sun has set last time.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site)
      return song_site.previous_setting(sun)
    
   def sun_set_next(self):
      """
         @brief: This function will determine when the Sun sets next time.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site)
      return song_site.next_setting(sun)

   def ast_twi_stop_next(self):

	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev
	song_site.horizon = "-12:"

	sun = ephem.Sun()
	sun.compute(song_site)
	return song_site.next_rising(sun)

   def obs_stop_next(self, sun_altitude):

	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev
	song_site.horizon = str(sun_altitude)+":"

	sun = ephem.Sun()
	sun.compute(song_site)
	return song_site.next_rising(sun)

   def sun_dist(self, star_ra, star_dec):
	"""
	 @brief: This function calculates projected distance from the Sun to a given object on the sky.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	sun = ephem.Sun()
	sun.compute(song_site)

#	star = ephem.readdb('star,f|A0,'+str(star_ra)+','+str(star_dec)+',2000')

	if len(str(star_ra).split(":")) == 1:
		star_ra = song_convert_coor.COOR_CONVERTER().convert_ra(star_ra)
		star_dec = song_convert_coor.COOR_CONVERTER().convert_dec(star_dec)

	star = ephem.FixedBody()
	star._ra = star_ra
	star._dec = star_dec
	star.compute(song_site)
	sun_d = ephem.separation(star, sun)
	return sun_d
    
   def night(self):
      """
         @brief: This function will determine if it is night or day.
     
         @todo: Some additional return values for the different kinds of twilight.
      """        
      song_site = ephem.Observer()
      song_site.lat = self.obs_lat
      song_site.long = self.obs_lon
      song_site.elev = self.obs_elev
        
      sun = ephem.Sun()
      sun.compute(song_site)
        
      sun_alt1 = sun.alt
      sun_alt2 = string.split(str(sun_alt1), ':')
      sun_alt = sun_alt2[0]
        
      if float(sun_alt) > -18.0 and float(sun_alt) < 0.0: # Astronomical twilight ends when sun is under 18 degrees below the horizon.
         return 'twilight'
      elif float(sun_alt) < -18.0:
         return 'night'
      else:
         return 'day'

class moon_pos():
   """
      @brief: This class calculates parameters for the Moon.
   """        
   def __init__(self, site=1):
	self.obs_lat, self.obs_lon, self.obs_elev = site_values(site)

   def moon_alt(self):
	"""
	 @brief: This function calculates the altitude of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute(song_site)
	return moon.alt

   def moon_az(self):
	"""
	 @brief: This function calculates the azimuth of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute(song_site)
	return moon.az

   def moon_rise_pre(self):
	"""
	 @brief: This function calculates the last rising time of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute()

	rise_moon= song_site.previous_rising(moon)
	return rise_moon   

   def moon_rise_next(self):
	"""
	 @brief: This function calculates the next rising time of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute()
	rise_moon= song_site.next_rising(moon)
	return rise_moon  

   def moon_set_pre(self):
	"""
	 @brief: This function calculates the last setting time of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute(song_site)
	set_moon = song_site.previous_setting(moon)
	return set_moon 

   def moon_set_next(self):
	"""
	 @brief: This function calculates the next setting time of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute(song_site)
	set_moon= song_site.next_setting(moon)
	return set_moon 

   def moon_phase(self):
	"""
	 @brief: This function calculates the phase of the Moon.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

	moon = ephem.Moon()
	moon.compute(song_site)
	return moon.phase
    
   def moon_dist(self, star_ra, star_dec):
	"""
	 @brief: This function calculates projected distance from the Moon to a given object on the sky.

	 @param star_ra: The right ascension of a star given in the format: HH:MM:SS.
	 @param star_dec: The declination of a star given in the format: DD:MM:SS.
	"""        
	song_site = ephem.Observer()
	song_site.lat = self.obs_lat
	song_site.long = self.obs_lon
	song_site.elev = self.obs_elev

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
	return m_d
