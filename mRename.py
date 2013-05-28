import sys
import os
import datetime
import re
import shutil
import subprocess

p = re.compile(r'\d+')
#http://stackoverflow.com/questions/165713/how-do-i-provide-a-suffix-for-days-of-the-month
date_lookup_list = ["th","st","nd","rd","th",
                           "th","th","th","th","th"]
def get_date_desc(date_num):
	if date_num % 100 >= 11 and date_num % 100 <= 13:
		return "th"
	return date_lookup_list[date_num % 10]
	
def start():
	print('Enter the starting screenshot number')
	screen_num = int(input('-> '))
	print('Enter Name')
	name_temp = '%s_%%s.png' % input('-> ')
	#CHANGE THIS FOR A DIFFERENT DIRECTORY.
	screen_path = os.path.join(r'C:\Users\Zored\Pictures\smplayer_screenshots', '')
	blog_folder = os.path.join(r'C:\Users\Zored\Pictures\Blog')
	today = datetime.datetime.now()
	#We format the string to include th or tr or whatever else the day might need.
	folder_date = today.strftime('%d{0} %B %Y'.format(get_date_desc(today.day)))
	converted_path = os.path.join(blog_folder, folder_date)
	if os.path.exists(converted_path) is False:
		os.mkdir(converted_path)
	image_file_iter = (x for x in os.listdir(screen_path) if getnum(screen_num, x))
	#We need to move each one of the image files.
	new_file_list = []
	for index, old_name in enumerate(image_file_iter):
		new_name = name_temp % index
		file_path = shutil.copyfile(os.path.join(screen_path, old_name), os.path.join(converted_path, new_name))
		new_file_list.append(file_path)
		print_str = "{0} {1} {2} moved to {3}".format(index, old_name, new_name, file_path)
		print (print_str)
	os.chdir(converted_path)
	subprocess.call(['mogrify', '-format', 'jpg', '*.png'], shell = True)
	for png_file in new_file_list:
		os.remove(png_file)
	
#Parses a file to get the shot number.
def getnum(start_num, file_string):
	x = p
	if int(x.findall(file_string)[0]) >= start_num:
		return True
	return False
	
if __name__ == '__main__':
	start()