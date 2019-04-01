"""
   Created on Oct 20, 2010
        
   @author: madsfa
"""
import psycopg2
import time
import master_config as m_conf

class db_connection():
   """
      @brief: This class makes connections to the database and collects data.
   """
   def get_values(self, table, database, req_no):
      """
         @brief: This function collects data from given table in database to a specific observation request.

         @param table: The name of the table in the specified database.
         @param database: The name of the wanted database.
         @param req_no: The observation request number.
      """    

#      host = "192.168.66.65"	# Tenerife site
#      user = "postgres"
#      password = ""
      host = m_conf.db_host	# Tenerife site
      user = m_conf.db_user
      password = m_conf.db_password
      db = str(database)

      # Make the connection to the database
      conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password)) 
        
      #make a cursor-object. this will be used to interact with the database
      curr = conn.cursor()
        
      #execute som query using the cursor
      if req_no != '':
         curr.execute("SELECT * FROM %s WHERE req_no=%s" % (table, str(req_no))) # There is data in this on, db = "song"
      else:
         curr.execute("SELECT * FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s)" % (table,table)) # There is data in this on, db = "song"
        
      #the cursor stores the results from the latest query. fetch there
      #output = curr.fetchall()
      output = curr.fetchone()
        
      #close cursor and connection (actually the cursor is automatically closed, when the connection is)
      curr.close()
      conn.close()
        
      return output

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
      if results != None:
         for i in range(len(results)):
            res_dict[fields[i]] = results[i]
         return res_dict
      else:
         return None

   def get_fields_temps(self, curr, table_name, fields=[]):
      field_str = ''
      for field in fields:
         field_str += field
         field_str += ','
      field_str = field_str[0:-1]
	
      stmt = 'SELECT %s FROM %s WHERE box_id = 2 AND ins_at = (SELECT max(ins_at) FROM %s WHERE box_id = 2)' % (field_str, table_name, table_name)
      curr.execute(stmt)
      results = curr.fetchone()
      res_dict = {}
      if results != None:
         for i in range(len(results)):
            res_dict[fields[i]] = results[i]
         return res_dict
      else:
         return None


   def get_fields_req_no(self, curr, table_name, fields=[], req_no=""):

      field_str = ''
      for field in fields:
         field_str += field
         field_str += ','
      field_str = field_str[0:-1]
	
      stmt = 'SELECT %s FROM %s WHERE req_no = %s' % (field_str, table_name, str(req_no))
      curr.execute(stmt)
      results = curr.fetchone()
      res_dict = {}
      if results != None:
         for i in range(len(results)):
            res_dict[fields[i]] = results[i]
         return res_dict
      else:
         return None

   def get_fields_site01(self, table_name, fields=[]):

      host = m_conf.db_host	# Tenerife site
      user = m_conf.db_user
      password = m_conf.db_password
      db = m_conf.data_db

      conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, password)) 
      curr = conn.cursor()

      field_str = ''
      for field in fields:
         field_str += field
         field_str += ','
      field_str = field_str[0:-1]
	
      stmt = 'SELECT %s FROM %s WHERE ins_at = (SELECT max(ins_at) FROM %s)' % (field_str, table_name, table_name)
      curr.execute(stmt)
      results = curr.fetchone()
      res_dict = {}
      if results != None:
         for i in range(len(results)):
            res_dict[fields[i]] = results[i]
         return res_dict
      else:
         return None

