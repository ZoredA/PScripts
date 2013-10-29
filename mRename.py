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
        import configparser
        config = configparser.ConfigParser()
        #CHANGE THESE TO A DIFFERENT DIRECTORY.        
        config.read('rename.conf')
        self.screen_path = os.path.join(config['Settings']['screenshot path'], '')
        self.destination_path = os.path.join(config['Settings']['destination path'], '')

    #http://stackoverflow.com/questions/165713/how-do-i-provide-a-suffix-for-days-of-the-month  
    def get_date_desc(self, date_num):
        date_lookup_list = ["th","st","nd","rd","th",
                                   "th","th","th","th","th"]
        if date_num % 100 >= 11 and date_num % 100 <= 13:
            return "th"
        return date_lookup_list[date_num % 10]
        
    #Parses a file to get the shot number and returns true if in range.
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
        
    #Parses a file to get the shot number.
    def get_num(self, file_string):
        x = self.p
        file_num = int(x.findall(file_string)[0])
        return file_num
        
    #Goes through a collection of files and tries to find the largest possible integer.
    #This helps us ensure that we don't overwrite previous extracts with the same name but updated
    #number.
    def get_max_num(self, file_coll):
        x = self.p
        max = 0
        if isinstance(file_coll, str):
            file_coll = [file_coll]
        for file_string in file_coll:
            temp = x.findall(file_string)
            if not temp:
                continue
            file_num = int(temp[0])
            if file_num > max:
                max = file_num
        return max
    
    def get_input(self):
        print('Enter Name')
        self.folder_name = input('-> ')
        self.name_temp = '%s %%s.png' % self.folder_name
        print('Enter the starting screenshot number. If no number is set a value of 0 will be assumed.')
        self.start_num = input('-> ')
        if self.start_num:
            try:
                self.start_num = int(self.start_num)
            except ValueError:
                print('Please enter a valid integer for starting number')
                raise
        else:
            self.start_num = 0
            
        print('Enter the ending screenshot number. Enter nothing if you don\'t wish to specify a range.')
        self.end_num = input('-> ')
        if self.end_num:
            try:
                self.end_num = int(self.end_num)
            except ValueError:
                print("Enter a valid integer or nothing at all")
                raise
            if self.end_num < self.start_num:
                raise ValueError("Ending number can not be less than the starting number")
        else:
            self.end_num = None
            
        print('Enter y if you wish to delete the moved images')
        if (input('-> ') == 'y'):
            self.del_old = True
        else:
            self.del_old = False
            
    def move_files(self):
        image_file_iter = (x for x in os.listdir(self.screen_path) if self.check_num(x))
        today = datetime.datetime.now()
        #We format the string to include th or tr or whatever else the day might need.
        folder_date = today.strftime('%d{0} %B %Y'.format(self.get_date_desc(today.day)))
        converted_path = os.path.join(self.destination_path, folder_date, self.folder_name)
        existing_files = set()
        if os.path.exists(converted_path) is False:
            os.makedirs(converted_path)
        else:
            existing_files.update(os.listdir(converted_path))
        #We need to move each one of the image files.
        new_file_list = []
        index = self.get_max_num(existing_files) + 1
        for old_name in image_file_iter:
            new_name = self.name_temp % index
            if new_name in existing_files:
                print_str = "{0} {1} already exists in {2}. Skipping. This will be converted and deleted.".format(index, new_name, converted_path)
                print (print_str)
            else:
                old_path = os.path.join(self.screen_path, old_name)
                file_path = shutil.copyfile(old_path, os.path.join(converted_path, new_name))
                new_file_list.append(file_path)
                #print_str = "{0} {1} {2} moved to {3}".format(index, old_name, new_name, file_path)
                if self.del_old is True:
                    #We delete the file.
                    os.remove(old_path)
            index += 1
        
        #We assign this to two class variables at the end for a theoretical 
        #minor performance increase when working with large collections.
        self.converted_path = converted_path
        self.new_file_list = new_file_list
        
    def convert_files(self):
        os.chdir(self.converted_path)
        print("Done Moving. Calling mogrify.")
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