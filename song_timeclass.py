"""
   Created on Feb 15, 2010

   @author: madsfa

   @todo: This module should include Franks corrected time. And maybe a GPS time.
"""
import time
import decimal
import numpy
import datetime

class TimeClass(object):
   """
      @brief: This is a simple time class which gives the time in different formats.
   """
   def __init__(self, nm = 'Mads Fredslund Andersen'):
      """constructor"""
      self.name = nm # class instance data attribute

   def whattime(self):
      """
         @brief: This function returns the current local time in readable format.
      """
      tid = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

      return tid

   def timename(self):
      """
         @brief: This function returns the current gm time in readable format.
      """
      tid = time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime())

      return tid

   def movie_date_name(self):
      """
         @brief: This function returns the current gm time in readable format.
      """
      date_name = time.strftime("%Y-%m-%d", time.gmtime())

      return date_name

   def juliandate(self):
      """
         @brief: This function returns the current time in Julian date.
      """
      fix_point = 2440587.50000 # (Julian Date at 1970:01:01T00:00:00)
      now_time = time.time()/float(60.0*60.0*24.0)
      jdate = fix_point + now_time # time.time() giver tiden i sekunder siden 1971:01:01T00:00:00      
      return "%.7f" % jdate

   def obstimeUT_old(self):
      """
         @brief: This function returns the exact time in UT and outputs in format: YYYY:mm:ddTHH:MM:SS.
      """
      DATE_OBS = time.strftime("%Y-%m-%dT%H:%M:%S", (time.gmtime()))
      DATE_OBS = DATE_OBS +'.'+ str(time.time()).split('.')[1]
      return DATE_OBS

   def obstimeUT(self):
      """
         @brief: This function returns the exact time in UT and outputs in format: YYYY:mm:ddTHH:MM:SS.
      """

      now_time = datetime.datetime.utcnow()     
      DATE_OBS = str(now_time).replace(" ", "T")

      return DATE_OBS

   def obstimeUTC(self):
      """
         @brief: This function returns the exact time in UT and outputs in format: YYYY:mm:ddTHH:MM:SS.
      """

      DATE_OBS = datetime.datetime.utcnow()

      return DATE_OBS

   def obstimeJD(self):
      """
         @brief: This function returns the Julian date.
      """
      fix_point = 2440587.50000 # (Julian Date at 1970:01:01T00:00:00)
      now_time = time.time()/float(60.0*60.0*24.0)
      jdate = fix_point + now_time # time.time() giver tiden i sekunder siden 1971:01:01T00:00:00      
      return "%.7f" % jdate

   def obstimeMJD(self):
      """
         @brief: This function returns the modified Julian date.
      """
      fix_point = 2440587.50000 # (Julian Date at 1970:01:01T00:00:00)
      now_time = time.time()/float(60.0*60.0*24.0)
      jdate = fix_point + now_time # time.time() giver tiden i sekunder siden 1971:01:01T00:00:00 
      mjdate = jdate - 2400000.5 # Modified Julian Date     
      return "%.7f" % mjdate

   def TimeSleep(self, interval):
      """
         @brief: This function does the same as time.sleep() but can be used when time.sleep() does not work.
                 It relies on time.time() to work.
      """
      t1 = time.time()
      t = t1
      stop_time = t1 + interval
      while t < stop_time:
         t = time.time()
      return 1 

   def TimeSleep2(self, interval):
      time.sleep(interval)
      return 1




