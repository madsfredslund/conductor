import time
import psycopg2
import conductor_config as conf
import datetime
import master_config as m_conf
import song_timeclass
import song_convert_coor
import get_db_values

clock = song_timeclass.TimeClass()

def Update():
	"""
		@brief: This function will check all active programs in the pre_obs_spec to keep track on what has actually been observed of the ORs inserted
	"""
	if conf.use_only_soda == "yes":
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
			curr = conn.cursor()
			curr.execute("SELECT id, last_obs_attempt, last_req_no, total_times_observed, filler_nr_shots FROM soda.pre_obs_req WHERE target_active = True")
			number_of_active_projects = curr.rowcount
			print clock.timename(), "Number of active projects: ", number_of_active_projects
			active_projects = curr.fetchall()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e	
		else:
			if number_of_active_projects > 0:
				for line in active_projects:
					pre_obs_spec_id, timestamp, req_number, total_number_acquired, total_number_needed = line
					### Check status of the OR:
					#print line
					if req_number != None and str(req_number) != '0':
						print clock.timename(), line
				
						try:
							conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
							curr = conn.cursor()
							curr.execute("SELECT status, ins_at FROM obs_request_status_1 WHERE req_no = %s" % (int(req_number)))
							req_status = curr.fetchone()
							curr.close()
							conn.close()
						except Exception, e:
							print clock.timename(), " Error: ", e
							return "error"	

						if req_status == None:
							if conf.update_or_status == "yes":
								conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
								curr = conn.cursor()

								try:
									stmt = "UPDATE soda.projects_target_definitions SET (last_req_no) = (0) WHERE id = %s" % (int(pre_obs_spec_id))
									curr.execute(stmt)
								except Exception as e:
									conn.rollback()
									return_value = e
							 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
									raise e
								else:		
									conn.commit()
									curr.close()
									conn.close()
									return 'done'

						if req_status[0] == "done":
							# The inserted observation was carried out and values must be updated!
							print clock.timename(), "Target was previously obseved %s times" % str(total_number_acquired)
		
							if total_number_acquired != None:
								total_number_acquired = int(total_number_acquired) + 1
							else:
								total_number_acquired = 1
					
							if total_number_needed != None:
								if total_number_acquired >= int(total_number_needed):
									active_state = False
									print clock.timename(), "The following target has finished..."
								else:
									active_state = True
							else:
								active_state = True

							if conf.update_or_status == "yes":
								conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
								curr = conn.cursor()

#								print clock.timename(), "Updating - observing project - (%i) with total acquired spectres (%i) and observed at (%s)" % (int(pre_obs_spec_id), int(total_number_acquired), str(req_status[1]))
							
								try:
									stmt = "UPDATE soda.projects_target_definitions SET (last_observed, total_times_observed, target_active, last_req_no) = ('%s', %s, '%s', 0) WHERE id = %s" % (req_status[1], total_number_acquired, active_state, int(pre_obs_spec_id))	
									print clock.timename(), stmt		
									curr.execute(stmt)
								except Exception as e:
									conn.rollback()
									return_value = e
							 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
									raise e
								else:		
									conn.commit()
									curr.close()
									conn.close()
									return 'done'	

						elif req_status[0] == "abort":
							# The inserted observation was carried out and values must be updated!
							if conf.update_or_status == "yes":
								conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
								curr = conn.cursor()

								try:
									stmt = "UPDATE soda.projects_target_definitions SET (last_req_no) = (0) WHERE id = %s" % (int(pre_obs_spec_id))
									curr.execute(stmt)
								except Exception as e:
									conn.rollback()
									return_value = e
							 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
									raise e
								else:		
									conn.commit()
									curr.close()
									conn.close()
									return 'done'	

						elif req_status[0] == "exec":
							print clock.timename(), "OR: %i is being executed" % (int(req_number))

	else:
		try:
			conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
			curr = conn.cursor()
			curr.execute("SELECT pre_obs_spec_id, ins_at, last_ins_req_no, total_number_acq, total_number_needed FROM pre_obs_spec WHERE active = True")
			number_of_active_projects = curr.rowcount
			print clock.timename(), "Number of active projects: ", number_of_active_projects
			active_projects = curr.fetchall()
			curr.close()
			conn.close()
		except Exception, e:
			print clock.timename(), " Error: ", e	 
		else:
			if number_of_active_projects > 0:
				for line in active_projects:
					pre_obs_spec_id, timestamp, req_number, total_number_acquired, total_number_needed = line
					### Check status of the OR:
					#print line
					if req_number != None and str(req_number) != '0':
				
						try:
							conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
							curr = conn.cursor()
							curr.execute("SELECT status, ins_at FROM obs_request_status_1 WHERE req_no = %i" % (int(req_number)))
							req_status = curr.fetchone()
							curr.close()
							conn.close()
						except Exception, e:
							print clock.timename(), " Error: ", e
							return "error"	

						if req_status[0] == "done":
							# The inserted observation was carried out and values must be updated!
							print clock.timename(), "Target was previously obseved %s times" % str(total_number_acquired)

							if total_number_acquired != None:
								total_number_acquired = int(total_number_acquired) + 1
							else:
								total_number_acquired = 1
					
							if total_number_needed != None:
								if total_number_acquired >= int(total_number_needed):
									active_state = False
									print clock.timename(), "The following target has finished..."
								else:
									active_state = True
							else:
								active_state = True

							if conf.update_or_status == "yes":
								conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
								curr = conn.cursor()

								print clock.timename(), "Updating - observing project - (%i) with total acquired spectres (%i) and observed at (%s)" % (int(pre_obs_spec_id), int(total_number_acquired), str(req_status[1]))

								try:
									stmt = "UPDATE pre_obs_spec SET (last_observed, total_number_acq, active, last_ins_req_no) = ('%s', %s, '%s', 0) WHERE pre_obs_spec_id = %s" % (req_status[1], total_number_acquired, active_state, int(pre_obs_spec_id))
					#				stmt = "UPDATE pre_obs_spec SET (last_observed, total_number_acq, active) = ('%s', %s, '%s') WHERE pre_obs_spec_id = %s" % (req_status[1], total_number_acquired, active_state, int(pre_obs_spec_id))
									curr.execute(stmt)
								except Exception as e:
									conn.rollback()
									return_value = e
							 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
									raise e
								else:		
									conn.commit()
									curr.close()
									conn.close()
									return 'done'	

						elif req_status[0] == "abort":
							# The inserted observation was carried out and values must be updated!
							if conf.update_or_status == "yes":
								conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
								curr = conn.cursor()

								try:
									stmt = "UPDATE pre_obs_spec SET (last_ins_req_no) = (0) WHERE pre_obs_spec_id = %s" % (int(pre_obs_spec_id))
									curr.execute(stmt)
								except Exception as e:
									conn.rollback()
									return_value = e
							 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
									raise e
								else:		
									conn.commit()
									curr.close()
									conn.close()
									return 'done'

						elif req_status[0] == "exec":
							print clock.timename(), "OR: %i is being executed" % (int(req_number))

	return "done"

def update_ongoing_or():

	if conf.use_only_soda == "yes":
			try:
				conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.data_db, m_conf.db_user, m_conf.db_password))
				curr = conn.cursor()
				curr.execute("SELECT req_no, ins_at FROM obs_request_status_1 WHERE status = 'exec'")
				or_status = curr.fetchone()
				curr.close()
				conn.close()
			except Exception, e:
				print clock.timename(), " Error: ", e
				return "error"

			if or_status != None:
				try:
					t_dif = datetime.datetime.utcnow() - or_status[1]
					if t_dif.seconds < 90:
						print clock.timename(), " Executing OR might still fail in acquisition..."
						return 1
				except Exception,e:
					print e
 
				print clock.timename(), " OR = %s is being executed and should now be updated" % (str(or_status[0]))
				try:
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.db_c_host, m_conf.or_db, m_conf.db_user, m_conf.db_password))
					curr = conn.cursor()	
					curr.execute("SELECT object_name, req_no, obs_mode, project_id, slit, iodine_cell, req_chain_previous FROM obs_request_1 WHERE req_no=%s" % (or_status[0]))
					output = curr.fetchone()
				except Exception,e:
					print e

				if conf.use_only_soda == "yes":					
					if int(output[6]) == 0:
						try:
							conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
							curr = conn.cursor()

							if output[2] == "none-iodine":
								obs_mode = "thar"
							else:
								obs_mode = output[2]

							if float(output[5]) == 1.0:
								obs_mode = "test-iodine"

							curr.execute("SELECT id FROM soda.pre_obs_req WHERE object_name='%s' AND obs_mode='%s' AND projectid=%s AND slit=%s AND target_active=True" % (output[0], obs_mode, output[3], output[4]))
						
							project_data = curr.fetchone()
							curr.close()
							conn.close()
						except Exception, e:
							print clock.timename(), " Error: ", e	
					elif int(output[6]) > 0:
						project_data = [output[6]]
					else:
						project_data = None
				
				if conf.update_or_status == "yes" and project_data != None:
					conn = psycopg2.connect("host='%s' dbname='%s' user='%s' password='%s'" % (m_conf.soda_host, m_conf.soda_db, m_conf.soda_user, m_conf.soda_pw))
					curr = conn.cursor()
				
					try:
						#stmt = "UPDATE soda.projects_target_definitions SET (last_observed, last_req_no) = ('%s', %s) WHERE id = %s" % (or_status[1], or_status[0], int(project_data[0]))	
						stmt = "UPDATE soda.projects_target_definitions SET (last_observed, last_req_no) = ('%s', %s) WHERE id = %s" % (str(datetime.datetime.utcnow()).split(".")[0], or_status[0], int(project_data[0]))	
						print clock.timename(), "Updating ongoing OR: - ", stmt		
						curr.execute(stmt)
					except Exception as e:
						conn.rollback()
						return_value = e
				 		print clock.timename(), "Could not update last_observed value. Changes to the status-data has been rolled back."
						raise e
					else:		
						conn.commit()
						curr.close()
						conn.close()

				elif conf.update_or_status == "yes" and project_data == None:
					print clock.timename(), "Could not find the correct target id in SODA where object_name='%s', obs_mode='%s', projectid=%s, slit=%s" % (output[0], obs_mode, output[3], output[4])

	return 1	





	
