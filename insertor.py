import time
import psycopg2
import conductor_config as conf
import datetime
import master_config as m_conf
import song_timeclass
import song_convert_coor
import get_db_values
import song_star_checker
import ephem
import numpy

sun_handle = song_star_checker.sun_pos()

clock = song_timeclass.TimeClass()


def insert_OR(pre_obs_spec_id="", gap=[]):
	### Collect data to create the OR

	OR_data = get_star_data(pre_obs_spec_id=pre_obs_spec_id)

	starid, pre_obs_spec_id, last_observed, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, project_id, read_out_mode, ra, decl, object_name, vmag, pm_ra, pm_decl, timecritical_tstart, timecritical_tend, schedule_type = OR_data
	project_data = get_project_data(project_id=project_id)

	project_name, project_id, first_name, last_name = project_data

	pi = first_name + " " + last_name

	if schedule_type == "timecritical":
		req_prio = 99
	elif schedule_type == "rv-standard":
		req_prio = 75
	elif schedule_type == "largeprogram":
		req_prio = 50
	elif schedule_type == "periodical":
		req_prio = 25
	elif schedule_type == "filler":
		req_prio = 2
	else:
		req_prio = 1


	epoch = 2000
	imagetype = "STAR"
	observer = pi
	project_name = project_name
	project_id = project_id
	x_bin = 1
	y_bin = 1
	x_begin = 1
	y_begin = 1
	x_end = 2088
	y_end = 2048
	ang_rot_offset = 0
	adc_mode = "false"

	if obs_mode.lower() == "iodine":
		iodine_cell = 3
	elif obs_mode.lower() == "none-iodine": 
		iodine_cell = 2
	elif obs_mode.lower() == 'thar':
		obs_mode = 'none-iodine'
		iodine_cell = 2
	elif obs_mode.lower() == "test-iodine":
		iodine_cell = 1
		obs_mode = "iodine"
	else:
		print obs_mode

	if nr_target_exp == None:
		nr_target_exp = 0
	if nr_thar_exp == None:
		nr_thar_exp = 0

	start_window = (gap[0] - datetime.timedelta(seconds=float(conf.insert_time_before))).strftime('%Y-%m-%d %H:%M:%S')	# set start_window to be 2 minutes before start of gap to account for corrections in the calculated gaps.
	stop_window = (gap[1] + datetime.timedelta(seconds=float(5*60))).strftime('%Y-%m-%d %H:%M:%S') # set stop_window to be 2 minutes after end of gap to allow observations to finish if needed.

	constraint_1 = 0
	constraint_2 = 0
	constraint_3 = 0
	constraint_4 = ""
	constraint_5 = ""
	req_chain_previous = int(pre_obs_spec_id)	# Now using this value for soda ID

	## Allow more than 1000 spectre per OR:
	if nr_exp > 1000 and nr_exp <= 10000:
		nr_exp = int(nr_exp / 10.)
 		req_chain_next = 10
	else:
		req_chain_next = 0

	site = 1
	ins_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

	insert_msg = "INSERT INTO obs_request_1 (right_ascension, declination, object_name, magnitude, ra_pm, dec_pm, obs_mode, exp_time, no_exp, no_target_exp, no_thar_exp, amp_gain, readoutmode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at) VALUES (%s, %s, '%s', %s, %s, %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, '%s', %s, '%s', '%s', %s, %s, %s, '%s', '%s', %s, %s, %s, '%s' )" % (ra / 15., decl, object_name, vmag, pm_ra, pm_decl, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, 2, read_out_mode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at)

	#### HERE THE OR SHOULD BE INSERTED ###

	if conf.insert_ors == "yes":

		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			curr.execute(insert_msg)
			conn.commit()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e	
		else:
			print clock.timename(), "An OR was inserted to fill the gap..."

			time.sleep(3)

			# This returns the request number of the request just inserted. 
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()

			try:
				or_req_tmp = get_db_values.db_connection().get_fields(curr, m_conf.or_table, fields=['req_no'])
				req_no = or_req_tmp['req_no']
			except Exception as e:
				conn.rollback()
				print clock.timename(), "Could not get OR from the database. Call has been rolled back."
				return_value = e

			curr.close()
		     	conn.close() 

			# now inserting the status of the OR....
			or_status_values = "( %i, '%s', '%s' )" % (int(req_no), "wait", datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()

			params = '(req_no, status, ins_at)'
			print clock.timename(), "Now inserting status=wait for OR: ", int(req_no) 
			try:
				stmt = "INSERT INTO obs_request_status_1 %s VALUES %s" % (params, or_status_values)
				curr.execute(stmt)
			except Exception as e:
				conn.rollback()
				return_value = e
		 		print clock.timename(), "Could not create status in the database. Changes to the status-data has been rolled back."
				raise e
			else:
				return_value = 'done'
			  

			conn.commit()
			curr.close()
		     	conn.close()  

			############### UPDATE OBSERVATION PARAMETERS in the pre_obs_spec table ##################

			# Now updating the pre_obs_spec table....
			if conf.use_only_soda == "yes":
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
				curr = conn.cursor()

				try:
					stmt = "UPDATE soda.projects_target_definitions SET (last_req_no, last_obs_attempt) = (%i, '%s') WHERE id = %s" % (int(req_no), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), int(pre_obs_spec_id))	
					#print stmt
					curr.execute(stmt)
				except Exception as e:
					conn.rollback()
					return_value = e
			 		print clock.timename(), "Could not update last_observed value. Changes to the project-data has been rolled back."
					raise e
				else:
					print clock.timename(), "The pre_obs_req table was updated..."
					return_value = 'done'
				  

				conn.commit()
				curr.close()
			     	conn.close()  
			else:
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
				curr = conn.cursor()

				try:
					stmt = "UPDATE pre_obs_spec SET (last_ins_req_no, ins_at) = (%s, '%s') WHERE pre_obs_spec_id = %s" % (int(req_no), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), str(pre_obs_spec_id))
					#print stmt
					curr.execute(stmt)
				except Exception as e:
					conn.rollback()
					return_value = e
			 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
					raise e
				else:
					print clock.timename(), "The pre_obs_spec table was updated..."
					return_value = 'done'
				  

				conn.commit()
				curr.close()
			     	conn.close()  
	else:
		print insert_msg

	print clock.timename(), "Now sleeping 10 seconds to make sure the OR and status are replicated before checking again."
	time.sleep(10)

	return 1


def insert_timecritical_OR(pre_obs_spec_id=""):
	### Collect data to create the OR

	OR_data = get_star_data(pre_obs_spec_id=pre_obs_spec_id)

	starid, pre_obs_spec_id, last_observed, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, project_id, read_out_mode, ra, decl, object_name, vmag, pm_ra, pm_decl, timecritical_tstart, timecritical_tend, schedule_type = OR_data
	project_data = get_project_data(project_id=project_id)

	project_name, project_id, first_name, last_name = project_data

	pi = first_name + " " + last_name

	req_prio = 99
	epoch = 2000
	imagetype = "STAR"
	observer = pi
	project_name = project_name
	project_id = project_id
	x_bin = 1
	y_bin = 1
	x_begin = 1
	y_begin = 1
	x_end = 2088
	y_end = 2048
	ang_rot_offset = 0
	adc_mode = "false"

	if obs_mode.lower() == "iodine":
		iodine_cell = 3
	elif obs_mode.lower() == "none-iodine": 
		iodine_cell = 2
	elif obs_mode.lower() == 'thar':
		obs_mode = 'none-iodine'
		iodine_cell = 2
	elif obs_mode.lower() == "test-iodine":
		iodine_cell = 1
		obs_mode = "iodine"
	else:
		print obs_mode

	if nr_target_exp == None:
		nr_target_exp = 0
	if nr_thar_exp == None:
		nr_thar_exp = 0

	start_window = (timecritical_tstart - datetime.timedelta(seconds=float(120))).strftime('%Y-%m-%d %H:%M:%S')	# set start_window to be 2 minutes before start of gap to account for corrections in the calculated gaps.
	stop_window = (timecritical_tend + datetime.timedelta(seconds=float(5*60))).strftime('%Y-%m-%d %H:%M:%S') # set stop_window to be 5 minutes after end of gap to allow observations to finish if needed.

	constraint_1 = 0
	constraint_2 = 0
	constraint_3 = 0
	constraint_4 = ""
	constraint_5 = ""
	req_chain_previous = int(pre_obs_spec_id)	# Now using this value for soda ID
	req_chain_next = 0
	site = 1
	ins_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


	insert_msg = "INSERT INTO obs_request_1 (right_ascension, declination, object_name, magnitude, ra_pm, dec_pm, obs_mode, exp_time, no_exp, no_target_exp, no_thar_exp, amp_gain, readoutmode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at) VALUES (%s, %s, '%s', %s, %s, %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, '%s', %s, '%s', '%s', %s, %s, %s, '%s', '%s', %s, %s, %s, '%s' )" % (ra / 15., decl, object_name, vmag, pm_ra, pm_decl, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, 2, read_out_mode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at)

	#### HERE THE OR SHOULD BE INSERTED ###

	if conf.insert_timecritical == "yes":

		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			curr.execute(insert_msg)
			conn.commit()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e	
		else:
			print clock.timename(), "An OR was inserted to fill the gap..."

			time.sleep(3)

			# This returns the request number of the request just inserted. 
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()

			try:
				or_req_tmp = get_db_values.db_connection().get_fields(curr, m_conf.or_table, fields=['req_no'])
				req_no = or_req_tmp['req_no']
			except Exception as e:
				conn.rollback()
				print clock.timename(), "Could not get OR from the database. Call has been rolled back."
				return_value = e

			curr.close()
		     	conn.close() 

			# now inserting the status of the OR....
			or_status_values = "( %i, '%s', '%s' )" % (int(req_no), "wait", datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()

			params = '(req_no, status, ins_at)'
			print clock.timename(), "Now inserting status=wait for OR: ", int(req_no) 
			try:
				stmt = "INSERT INTO obs_request_status_1 %s VALUES %s" % (params, or_status_values)
				curr.execute(stmt)
			except Exception as e:
				conn.rollback()
				return_value = e
		 		print clock.timename(), "Could not create status in the database. Changes to the status-data has been rolled back."
				raise e
			else:
				return_value = 'done'
			  

			conn.commit()
			curr.close()
		     	conn.close()  

			############### UPDATE OBSERVATION PARAMETERS in the pre_obs_spec table ##################

			# Now updating the pre_obs_spec table....
			if conf.use_only_soda == "yes":
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
				curr = conn.cursor()

				try:
					stmt = "UPDATE soda.projects_target_definitions SET (last_req_no, last_obs_attempt) = (%i, '%s') WHERE id = %s" % (int(req_no), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), int(pre_obs_spec_id))	
					print stmt
					curr.execute(stmt)
				except Exception as e:
					conn.rollback()
					return_value = e
			 		print clock.timename(), "Could not update last_observed value. Changes to the project-data has been rolled back."
					raise e
				else:
					print clock.timename(), "The pre_obs_req table was updated..."
					return_value = 'done'
				  

				conn.commit()
				curr.close()
			     	conn.close()  
			else:
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
				curr = conn.cursor()

				try:
					stmt = "UPDATE pre_obs_spec SET (last_ins_req_no, ins_at) = (%s, '%s') WHERE pre_obs_spec_id = %s" % (int(req_no), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), str(pre_obs_spec_id))
					print stmt
					curr.execute(stmt)
				except Exception as e:
					conn.rollback()
					return_value = e
			 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
					raise e
				else:
					print clock.timename(), "The pre_obs_spec table was updated..."
					return_value = 'done'
				  

				conn.commit()
				curr.close()
			     	conn.close()  
	else:
		print insert_msg

	print clock.timename(), "Now sleeping 10 seconds to make sure the OR and status are replicated before checking again."
	time.sleep(10)

	return 1


def get_star_data(pre_obs_spec_id=""):
	"""
	@brief: Reading the database for relevant observations
	"""
	### Collect the 
#	print clock.timename(), "Collecting data for the star and observations for starid = %s" % (str(star_id))
	if conf.use_only_soda == "yes":
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
			curr = conn.cursor()
			curr.execute("SELECT starid, id, last_observed, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, projectid, readout_mode, ra, decl, object_name, vmag, pm_ra, pm_decl,timecritical_tstart, timecritical_tend, schedule_type FROM soda.pre_obs_req WHERE id = %s" % (str(pre_obs_spec_id)))
			OR_data = curr.fetchone()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e

	else:

		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			curr.execute("SELECT starid, pre_obs_spec_id, last_observed, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, project_id, read_out_mode FROM pre_obs_spec WHERE pre_obs_spec_id = %s" % (str(pre_obs_spec_id)))				
			obs_data = curr.fetchone()
			numb_of_rows = curr.rowcount
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e
		else:
			if numb_of_rows > 0:
		
				try:
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
					curr = conn.cursor()
					curr.execute("SELECT ra, decl, object_name, vmag, pm_ra, pm_decl, starid FROM soda.stars WHERE starid = %s " % (str(obs_data[0])))
					stars_data = curr.fetchone()
					curr.close()
					conn.close()
				except Exception, e:
					print clock.timename(), " Error: ", e
				else:
					obs_data = obs_data + stars_data[:-1]

### obs_data: starid, pre_obs_spec_id, last_observed, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, project_id, read_out_mode, ra, decl, object_name, vmag, pm_ra, pm_decl
              
				return obs_data
			else:
				print clock.timename(), "No stars were observable at this hour..."

	return OR_data

def get_project_data(project_id=""):
	"""
	@brief: Reading the database for relevant observations
	"""
	### Collect the 
#	print clock.timename(), "Collecting data for the project with project_id = %s" % (str(project_id))

	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
		curr = conn.cursor()
		curr.execute("SELECT projectname, projectid, first_name, last_name FROM soda.projects INNER JOIN soda.users ON soda.users.userid = soda.projects.pi WHERE projectid = %s" % (str(project_id)))
		project_data = curr.fetchone()
		curr.close()
		conn.close()
	except Exception, e:
		print clock.timename(), " Error: ", e

	return project_data

def update_star_data(star_id=""):
	### UPDATE THE parameters for the special type of observations ###


	return 1

def insert_solar_observations(project_id=3):
	"""
	@brief: Reading the database for relevant observations
	"""
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
		curr = conn.cursor()
		curr.execute("SELECT object_name, Vmag, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, amp_gain, read_out_mode, slit, project_id FROM pre_obs_spec INNER JOIN stars ON stars.starid = pre_obs_spec.starid WHERE project_id = %s" % (str(project_id)))
		OR_data = curr.fetchall()
		curr.close()
		conn.close()
	except Exception, e:
		print clock.timename(), " Error: ", e
	else:	
		for line in OR_data:
			object_name, Vmag, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, amp_gain, read_out_mode, slit, project_id = line

			try:
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
				curr = conn.cursor()
				curr.execute("SELECT pi, name, project_id FROM projects WHERE project_id = %s" % (str(project_id)))
				project_data = curr.fetchone()
				curr.close()
				conn.close()
			except Exception, e:
				print clock.timename(), " Error: ", e

			#### INSERT BOTH ORs:

			pi, project_name, project_id = project_data

			req_prio = 1
			epoch = 2000
			imagetype = "STAR"
			observer = pi
			project_name = project_name
			project_id = project_id
			x_bin = 1
			y_bin = 1
			x_begin = 1
			y_begin = 1
			x_end = 2088
			y_end = 2048
			ang_rot_offset = 0
			adc_mode = "false"
			if obs_mode.lower() == "iodine":
				iodine_cell = 3
			elif obs_mode.lower() == "none-iodine": 
				iodine_cell = 2
			elif obs_mode.lower() == 'thar':
				obs_mode = 'none-iodine'
				iodine_cell = 2
			elif obs_mode.lower() == "test-iodine":
				iodine_cell = 1
			else:
				print obs_mode

			start_window = datetime.datetime.strptime(str(sun_handle.sun_set_next()).replace("/", "-"), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=(3600*2))
			stop_window = datetime.datetime.strptime(str(sun_handle.sun_set_next()).replace("/", "-"), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=(3600))

			constraint_1 = 0
			constraint_2 = 0
			constraint_3 = 0
			constraint_4 = ""
			constraint_5 = ""
			req_chain_previous = 0
			req_chain_next = 0
			site = 1
			ins_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

			# Get telescope current pointing position:
			#tel_point = get_db_values.db_connection().get_fields_site01("tel_dome", fields=["tel_ra", "tel_dec"])

			pm_ra = 0.0
			pm_decl = 0.0
			ra = 0.0
			decl = 0.0
			Vmag = -5.0

			insert_msg = "INSERT INTO obs_request_1 (right_ascension, declination, object_name, magnitude, ra_pm, dec_pm, obs_mode, exp_time, no_exp, no_target_exp, no_thar_exp, amp_gain, readoutmode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at) VALUES (%s, %s, '%s', %s, %s, %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, '%s', %s, '%s', '%s', %s, %s, %s, '%s', '%s', %s, %s, %s, '%s' )" % (ra, decl, object_name, Vmag, pm_ra, pm_decl, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, amp_gain, read_out_mode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at)

			#### HERE THE OR SHOULD BE INSERTED ###

			if conf.insert_solar_ors == "yes":

				try:
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()
					curr.execute(insert_msg)
					conn.commit()
					curr.close()
					conn.close()
				except Exception, e:
					print clock.timename(), " Error: ", e	
				else:
					print clock.timename(), "An OR was inserted"

					time.sleep(3)

					# This returns the request number of the request just inserted. 
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()

					try:
						or_req_tmp = get_db_values.db_connection().get_fields(curr, m_conf.or_table, fields=['req_no'])
						req_no = or_req_tmp['req_no']
					except Exception as e:
						conn.rollback()
						print clock.timename(), "Could not get OR from the database. Call has been rolled back."
						return_value = e

					curr.close()
				     	conn.close() 

					# now inserting the status of the OR....
					or_status_values = "( %i, '%s', '%s' )" % (int(req_no), "wait", datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()

					params = '(req_no, status, ins_at)'

					try:
						stmt = "INSERT INTO obs_request_status_1 %s VALUES %s" % (params, or_status_values)
						curr.execute(stmt)
					except Exception as e:
						conn.rollback()
						return_value = e
				 		print clock.timename(), "Could not create status in the database. Changes to the status-data has been rolled back."
					else:
						return_value = 'done'					  

					conn.commit()
					curr.close()
				     	conn.close()  
			else:
				print insert_msg
								



def insert_solar_observations_soda(project_id=115, starid=0):
	"""
	@brief: Reading the soda database for relevant observations
	"""

	song_site = ephem.Observer()
	song_site.lat = conf.lat_obs
	song_site.long = conf.lon_obs
	song_site.elev = conf.elev_obs

	song_site.date = datetime.datetime.utcnow()

	sun = ephem.Sun()
	sun.compute(song_site)

	sun_next_set = song_site.next_setting(sun)
	sun_pre_rise = song_site.previous_rising(sun)

	pre_sun_rise = datetime.datetime.strptime(str(sun_pre_rise), "%Y/%m/%d %H:%M:%S")
	next_sun_set = datetime.datetime.strptime(str(sun_next_set), "%Y/%m/%d %H:%M:%S")

	time_diff = next_sun_set - pre_sun_rise


#### Synoptic visits each day

	def calc_times(pre_sun_rise):

		tnoon = pre_sun_rise + datetime.timedelta(seconds=(time_diff.seconds)/2)
		#print str(tnoon)

		obs_times = [tnoon + datetime.timedelta(hours = x) for x in conf.solar_times]
		#obs_times = [tnoon - datetime.timedelta(hours = 2), tnoon, tnoon + datetime.timedelta(hours = 2)]

		return obs_times


	observing_times = calc_times(pre_sun_rise)

	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
		curr = conn.cursor()
		curr.execute("SELECT object_name, vmag, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, projectid, id, readout_mode FROM soda.pre_obs_req WHERE projectid = %s and starid=%s and schedule_type='periodical' AND target_active = True AND active = True" % (str(project_id), str(starid)))
		OR_data = curr.fetchall()
		curr.close()
		conn.close()
	except Exception, e:
		print clock.timename(), " Error: ", e
	else:	
		for observing_time in observing_times:

			for line in OR_data:
				object_name, Vmag, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, project_id, pre_obs_spec_id, read_out_mode = line

				print line

				project_data = get_project_data(project_id=project_id)
				project_name, project_id, first_name, last_name = project_data

				pi = first_name + " " + last_name

				req_prio = 1
				epoch = 2000
				imagetype = "STAR"
				observer = pi
				project_name = project_name
				project_id = project_id
				x_bin = 1
				y_bin = 1
				x_begin = 1
				y_begin = 1
				x_end = 2088
				y_end = 2048
				ang_rot_offset = 0
				adc_mode = "false"
				if obs_mode.lower() == "iodine":
					iodine_cell = 3
				elif obs_mode.lower() == "none-iodine": 
					iodine_cell = 2
				elif obs_mode.lower() == 'thar':
					obs_mode = 'none-iodine'
					iodine_cell = 2
				elif obs_mode.lower() == "test-iodine":
					iodine_cell = 1
					obs_mode = "iodine"

				if nr_target_exp == None:
					nr_target_exp = 0
				if nr_thar_exp == None:
					nr_thar_exp = 0

				start_window = datetime.datetime.strptime(str(observing_time), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=((float(nr_exp) * float(exp_time)) / 2 + 120)) # 120 seconds overhead
				stop_window = datetime.datetime.strptime(str(observing_time), "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=(int(float(nr_exp) * float(exp_time)) + 300)) # 5 min overhead

				constraint_1 = 0
				constraint_2 = 0
				constraint_3 = 0
				constraint_4 = "sun-fibre"
				constraint_5 = ""
				req_chain_previous = int(pre_obs_spec_id)	# Now using this value for soda ID
				req_chain_next = 0
				site = 1
				ins_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

				# Get telescope current pointing position:
				#tel_point = get_db_values.db_connection().get_fields_site01("tel_dome", fields=["tel_ra", "tel_dec"])

				pm_ra = 0.0
				pm_decl = 0.0
				ra = 0.0
				decl = 0.0
				Vmag = -5.0

				insert_msg = "INSERT INTO obs_request_1 (right_ascension, declination, object_name, magnitude, ra_pm, dec_pm, obs_mode, exp_time, no_exp, no_target_exp, no_thar_exp, amp_gain, readoutmode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at) VALUES (%s, %s, '%s', %s, %s, %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, '%s', %s, '%s', '%s', %s, %s, %s, '%s', '%s', %s, %s, %s, '%s' )" % (ra, decl, object_name, Vmag, pm_ra, pm_decl, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, 2, read_out_mode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at)

				#### HERE THE OR SHOULD BE INSERTED ###

				if conf.insert_solar_synopic == "yes":

					try:
						conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
						curr = conn.cursor()
						curr.execute(insert_msg)
						conn.commit()
						curr.close()
						conn.close()
					except Exception, e:
						print clock.timename(), " Error: ", e	
					else:
						print clock.timename(), "An OR was inserted"

						time.sleep(3)

						# This returns the request number of the request just inserted. 
						conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
						curr = conn.cursor()

						try:
							or_req_tmp = get_db_values.db_connection().get_fields(curr, m_conf.or_table, fields=['req_no'])
							req_no = or_req_tmp['req_no']
						except Exception as e:
							conn.rollback()
							print clock.timename(), "Could not get OR from the database. Call has been rolled back."
							return_value = e

						curr.close()
					     	conn.close() 

						# now inserting the status of the OR....
						or_status_values = "( %i, '%s', '%s' )" % (int(req_no), "wait", datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

						conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
						curr = conn.cursor()

						params = '(req_no, status, ins_at)'

						try:
							stmt = "INSERT INTO obs_request_status_1 %s VALUES %s" % (params, or_status_values)
							curr.execute(stmt)
						except Exception as e:
							conn.rollback()
							return_value = e
					 		print clock.timename(), "Could not create status in the database. Changes to the status-data has been rolled back."
						else:
							return_value = 'done'					  

						conn.commit()
						curr.close()
					     	conn.close()  
				else:
					print insert_msg


	#### High cadence Solar observations:
	try:
		conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
		curr = conn.cursor()
		curr.execute("SELECT object_name, vmag, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, projectid, id, readout_mode FROM soda.pre_obs_req WHERE projectid = %s and starid=%s and schedule_type='largeprogram' AND target_active = True AND active = True" % (str(project_id), str(starid)))
		OR_data = curr.fetchall()
		curr.close()
		conn.close()
	except Exception, e:
		print clock.timename(), " Error: ", e
	else:	

		for line in OR_data:
			object_name, Vmag, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, slit, project_id, pre_obs_spec_id, read_out_mode = line

			print line

			project_data = get_project_data(project_id=project_id)
			project_name, project_id, first_name, last_name = project_data

			pi = first_name + " " + last_name

			req_prio = 1
			epoch = 2000
			imagetype = "STAR"
			observer = pi
			project_name = project_name
			project_id = project_id
			x_bin = 1
			y_bin = 1
			x_begin = 1
			y_begin = 1
			x_end = 2088
			y_end = 2048
			ang_rot_offset = 0
			adc_mode = "false"
			if obs_mode.lower() == "iodine":
				iodine_cell = 3
			elif obs_mode.lower() == "none-iodine": 
				iodine_cell = 2
			elif obs_mode.lower() == 'thar':
				obs_mode = 'none-iodine'
				iodine_cell = 2
			elif obs_mode.lower() == "test-iodine":
				iodine_cell = 1
				obs_mode = "iodine"

			if nr_target_exp == None:
				nr_target_exp = 0
			if nr_thar_exp == None:
				nr_thar_exp = 0

			start_window = pre_sun_rise # from sunrise
			stop_window = next_sun_set - datetime.timedelta(seconds=3600) # an hour before sunset

			constraint_1 = 0
			constraint_2 = 0
			constraint_3 = 0
			constraint_4 = "sun-fibre"
			constraint_5 = ""
			req_chain_previous = int(pre_obs_spec_id)	# Now using this value for soda ID
			
			if nr_exp > 1000:
				req_chain_next = int(numpy.ceil(nr_exp / 1000.))
				nr_exp = 1000
			else:
				req_chain_next = 0
			
			site = 1
			ins_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

			# Get telescope current pointing position:
			#tel_point = get_db_values.db_connection().get_fields_site01("tel_dome", fields=["tel_ra", "tel_dec"])

			pm_ra = 0.0
			pm_decl = 0.0
			ra = 0.0
			decl = 0.0
			Vmag = -5.0

			insert_msg = "INSERT INTO obs_request_1 (right_ascension, declination, object_name, magnitude, ra_pm, dec_pm, obs_mode, exp_time, no_exp, no_target_exp, no_thar_exp, amp_gain, readoutmode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at) VALUES (%s, %s, '%s', %s, %s, %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, '%s', %s, '%s', '%s', %s, %s, %s, '%s', '%s', %s, %s, %s, '%s' )" % (ra, decl, object_name, Vmag, pm_ra, pm_decl, obs_mode, exp_time, nr_exp, nr_target_exp, nr_thar_exp, 2, read_out_mode, slit, req_prio, epoch, imagetype, observer, project_name, project_id, x_bin, y_bin, x_begin, y_begin, x_end, y_end, ang_rot_offset, adc_mode, iodine_cell, start_window, stop_window, constraint_1, constraint_2, constraint_3, constraint_4, constraint_5, site, req_chain_previous, req_chain_next, ins_at)

			#### HERE THE OR SHOULD BE INSERTED ###

			if conf.insert_solar_synopic == "yes":

				try:
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()
					curr.execute(insert_msg)
					conn.commit()
					curr.close()
					conn.close()
				except Exception, e:
					print clock.timename(), " Error: ", e	
				else:
					print clock.timename(), "An OR was inserted"

					time.sleep(3)

					# This returns the request number of the request just inserted. 
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()

					try:
						or_req_tmp = get_db_values.db_connection().get_fields(curr, m_conf.or_table, fields=['req_no'])
						req_no = or_req_tmp['req_no']
					except Exception as e:
						conn.rollback()
						print clock.timename(), "Could not get OR from the database. Call has been rolled back."
						return_value = e

					curr.close()
				     	conn.close() 

					# now inserting the status of the OR....
					or_status_values = "( %i, '%s', '%s' )" % (int(req_no), "wait", datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()

					params = '(req_no, status, ins_at)'

					try:
						stmt = "INSERT INTO obs_request_status_1 %s VALUES %s" % (params, or_status_values)
						curr.execute(stmt)
					except Exception as e:
						conn.rollback()
						return_value = e
				 		print clock.timename(), "Could not create status in the database. Changes to the status-data has been rolled back."
					else:
						return_value = 'done'					  

					conn.commit()
					curr.close()
				     	conn.close()  
			else:
				print insert_msg
							



	

	
