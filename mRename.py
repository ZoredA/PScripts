import sys
import os
import datetime
import re
import shutil
import subprocess

class Rename():

	def __init__(self):
		self.p = re.compile(r'\d+')
		self.set_paths()
		
	def set_paths(self):							   
		#CHANGE THESE TO A DIFFERENT DIRECTORY.						   
		self.screen_path = os.path.join(r'C:\Users\Zored\Pictures\smplayer_screenshots', '')
		self.destination_path = os.path.join(r'C:\Users\Zored\Pictures\ConvertedShots')

	#http://stackoverflow.com/questions/165713/how-do-i-provide-a-suffix-for-days-of-the-month	
	def get_date_desc(self, date_num):
		date_lookup_list = ["th","st","nd","rd","th",
								   "th","th","th","th","th"]
		if date_num % 100 >= 11 and date_num % 100 <= 13:
			return "th"
		return date_lookup_list[date_num % 10]
		
	#Parses a file to get the shot number.
	def check_num(self, file_string):
		x = self.p
		file_num = int(x.findall(file_string)[0])
		if self.end_num is None:
			if  file_num >= self.start_num:
				return True
		else:
			if file_num >= self.start_num and file_num <= self.end_num:
				return True
		return False

	def get_input(self):
		print('Enter Name')
		self.name_temp = '%s_%%s.png' % input('-> ')
		print('Enter the starting screenshot number')
		try:
			self.start_num = int(input('-> '))
		except ValueError:
			print('Please enter a valid integer for starting number')
			raise
			
		print('Enter the ending screenshot number. Enter nothing if you don\'t wish to specify a range.')
		self.end_num = input('-> ')
		if self.end_num:
			try:
				self.end_num = int(self.end_num)
			except ValueError:
				print("Enter a valid integer or nothing at all")
				raise
			if self.end_num < start_num:
				raise ValueError("Ending number can not be less than the starting number")
		else:
			self.end_num = None
			
	def move_files(self):
		image_file_iter = (x for x in os.listdir(self.screen_path) if self.check_num(x))
		today = datetime.datetime.now()
		#We format the string to include th or tr or whatever else the day might need.
		folder_date = today.strftime('%d{0} %B %Y'.format(self.get_date_desc(today.day)))
		converted_path = os.path.join(self.destination_path, folder_date)
		existing_files = set()
		if os.path.exists(converted_path) is False:
			os.mkdir(converted_path)
		else:
			existing_files.update(os.listdir(converted_path))
		#We need to move each one of the image files.
		new_file_list = []
		for index, old_name in enumerate(image_file_iter):
			new_name = self.name_temp % index
			if new_name in existing_files:
				print_str = "{0} {2} already exists in {3}. Skipping. This will be converted and deleted.".format(index, new_name, self.converted_path)
			else:
				file_path = shutil.copyfile(os.path.join(self.screen_path, old_name), os.path.join(converted_path, new_name))
				new_file_list.append(file_path)
				print_str = "{0} {1} {2} moved to {3}".format(index, old_name, new_name, file_path)
			print (print_str)
			
		
		#We assign this two class variables at the end for a theoretical 
		#minor performance increase when working with large collections.
		self.converted_path = converted_path
		self.new_file_list = new_file_list
		
	def convert_files(self):
		os.chdir(self.converted_path)
		subprocess.call(['mogrify', '-format', 'jpg', '*.png'], shell = True)
		
	def delete_files(self):
		for png_file in self.new_file_list:
			os.remove(png_file)
			
	def start(self):
		self.get_input()
		self.move_files()
		self.convert_files()
		self.delete_files()
	
if __name__ == '__main__':
	x = Rename()
	x.start()