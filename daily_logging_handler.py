import os
import song_timeclass

def handle_log_files(current_log_file, old_log_file):
	"""
		@brief: This function will copy the content of the current_log_file into old_log_fil and clear the current one. 
	"""
	error = 0
	try:
		#os.rename(current_log_file, old_log_file) 	# This 
		tmp_file_1 = file(current_log_file, "r")
		file_info = tmp_file_1.readlines()
		tmp_file_1.close()
		tmp_file_2 = file(old_log_file, "w")
		for line in file_info:
			tmp_file_2.write(str(line))
		tmp_file_2.close()
	except Exception, e:
		print e
		print "Could not rename %s file to %s" %(current_log_file, old_log_file)
		error = 1

	if error == 0:
		try:
			tmp_file = file(current_log_file, "w")
			text = "The content of %s was moved to %s at: %s\n\n" %  (current_log_file, old_log_file, song_timeclass.TimeClass().obstimeUT())
			tmp_file.write(text)
			tmp_file.close()
		except Exception, e:
			print "Could not clear %s" %(current_log_file)
			error = 1

	return error

