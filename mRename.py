import sys
import os
import datetime
import re
import shutil
import subprocess
import collections
import PrintDictionary
import RangeWorks

from colorama import init, Fore, Back, Style
rename_format_dict = \
    {
        'str_format': "{_COUNTER:<30} {folder_name} from {start_num} to {end_num}",
        'colors': \
            {
                'start_num': [Fore.GREEN,Style.BRIGHT],
                'end_num' : [Fore.RED,Style.BRIGHT],
                'folder_name' : [Fore.WHITE, Style.BRIGHT]
            },
        'count_start' : 1,
        'default' : [Fore.YELLOW, Back.BLACK, Style.BRIGHT],
        'str.format' : True,
    }
class Rename():

    def __init__(self):
        self.p = re.compile(r'\d+')
        self.set_paths()
        self.date = False
        
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
        tempList = x.findall(file_string)
        if not tempList:
            return False
        file_num = int(tempList[0])
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
            file_num = int(temp[-1])  #Look at the number at the end of the name. Gets rid of bugs like Log Horizon 2 48 being read as 2.
            if file_num > max:
                max = file_num
        return max
        
    def get_static_input(self):
        input_dict = {}
        print('Enter Name')
        input_dict['folder_name'] = input('-> ')
        print('Enter the starting screenshot number. If no number is set a value of 0 will be assumed.')
        input_dict['start_num'] = input('-> ')
        if input_dict['start_num']:
            try:
                input_dict['start_num'] = int(input_dict['start_num'])
            except ValueError:
                print('Please enter a valid integer for starting number')
                raise
        else:
            input_dict['start_num'] = 0
            
        print('Enter the ending screenshot number. Enter nothing if you don\'t wish to specify a range.')
        input_dict['end_num'] = input('-> ')
        if input_dict['end_num']:
            try:
                input_dict['end_num'] = int(input_dict['end_num'])
            except ValueError:
                print("Enter a valid integer or nothing at all")
                raise
            if input_dict['end_num'] < input_dict['start_num']:
                raise ValueError("Ending number can not be less than the starting number")
        else:
            input_dict['end_num'] = None

        return input_dict
        
    def get_input(self):
        input_dict = self.get_static_input()
        self.folder_name = input_dict['folder_name']
        self.name_temp = '%s %%s.png' % self.folder_name
        self.start_num = input_dict['start_num']
        self.end_num = input_dict['end_num']
        self.start_num = input_dict['start_num']
        
        print('Enter y if you wish to delete the moved images')
        if (input('-> ') == 'y'):
            self.del_old = True
        else:
            self.del_old = False
            
    def move_files(self):
        image_file_iter = (x for x in os.listdir(self.screen_path) if self.check_num(x))
        today = datetime.datetime.now()
        
        if self.date:
            #We format the string to include th or tr or whatever else the day might need.
            folder_date = today.strftime('%d{0} %B %Y'.format(self.get_date_desc(today.day)))
            converted_path = os.path.join(self.destination_path, folder_date, self.folder_name)
        else:
            converted_path = os.path.join(self.destination_path, self.folder_name)
        existing_files = set()
        if os.path.exists(converted_path) is False:
            os.makedirs(converted_path)
        else:
            existing_files.update(os.listdir(converted_path))
        #We need to move each one of the image files.
        new_file_list = []
        index = self.get_max_num(existing_files) + 1
        undeleted_files = []
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
                    #print("Deleting old files")
                    #We delete the file.
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        undeleted_files.append( (old_path, e) )
            index += 1
        if undeleted_files:
            #Assumes all of the exceptions were for the same problem.
            undeleted_files_list = [x[0] for x in undeleted_files]
            print("Files not deleted:")
            print(",".join(undeleted_files_list))
        
        #We assign this to two class variables at the end for a theoretical 
        #minor performance increase when working with large collections.
        self.converted_path = converted_path
        self.new_file_list = new_file_list
        
    #TO DO: Somehow get this to only call mogrify on the files we just moved and NOT all the .png files in
    #that folder....
    def convert_files(self):
        os.chdir(self.converted_path)
        print("Done Moving. Calling mogrify.")
        subprocess.call(['mogrify', '-format', 'jpg', '*.png'], shell = True)
        
    def delete_files(self):
        print("Deleting png files for run with name: %s" % self.folder_name )
        for png_file in self.new_file_list:
            os.remove(png_file)
    
    #This function moves many different images. It is pretty simple and a bit of a hack because it just does the same thing many times.
    #many_list is a list of dictionaries with each dictionary looking like this:
    # {
        # 'folder_name' : 'folder_name',
        # 'start_num' : start_num,
        # 'end_num' : end_num
    # }
    #end_num can be none and start_num should be 0 if no start num is needed.
    #to_del is obviously what determines whether the original files will be deleted or not.
    def start_many(self, many_list, del_old = False):
        self.del_old = del_old;
        #If many_list needs to be an iterable other than a string.
        if not isinstance(many_list, collections.Iterable) or isinstance(many_list, str):
            raise TypeError("Type Error. Expected an iterable but got %s." % type(many_list))
        for to_do_dict in many_list:
            self.folder_name = to_do_dict['folder_name']
            #We might already be getting an int but just in case, we are going to cast it again. If it is bad input, it will
            #get caught here.
            self.start_num = int(to_do_dict['start_num'])
            self.end_num = int(to_do_dict['end_num'])
            self.name_temp = '%s %%s.png' % self.folder_name
            self.run()
            
    def start(self):
        self.get_input()
        self.run()
        
    def run(self):
        self.move_files()
        self.convert_files()
        self.delete_files()

#Reads an input file and turns it into a list of dictionaries.
#Each item corresponds to one entry in the file and has three fields:
#folder_name, start_num and end_num
def parse_file(file_name):
    bad_chars = re.compile(r'[/\\?<>|]')
    #Starting at 0 should not cause problems because the Rename() just checks to see if
    #the current image number is greater than the starting number. It doesn't check to see if
    #the starting number is the same as 0.
    #TO DO: Add support for multiple image selections in one line.
        #e.g. Valvrave the Liberator : -45 :56 - 78: 122-
    many_list = []
    num_ranges = []
    with open(os.path.join('',file_name), 'r') as f_input:

        for count, line in enumerate(f_input):
            stripLine = line.strip()
            if not stripLine: continue
            if stripLine[0] == '#': continue
            if stripLine[0] == '\\': stripLine = stripLine.lstrip('\\')
            if bad_chars.search(stripLine):
                raise ValueError("Line: %s contains invalid characters (one of /\?<>| )." % strpLine)
            # Name = ''
            # N = 0
            # M = None
            temp_list = [x.strip() for x in stripLine.split(':') if x.strip()]
            temp_length = len(temp_list)
            if temp_length == 2:
                #We got a name as well as N or M or both.
                Name = temp_list[0]
                first_post_colon_char = temp_list[1][0]
                if not first_post_colon_char:
                    #We got (Name:). No M or N were specified.
                    N = 0
                    M = None
                elif first_post_colon_char == '-':
                    #We got just M. (Name: -M)
                    try:
                        M = int(temp_list[1][1:])
                    except:
                        print ("Bad line: %s with index : %s" % (line, count))
                        raise
                    N = 0
                else:
                    temp_list_two = [x.strip() for x in temp_list[1].split('-')]
                    temp_length_two = len(temp_list_two)
                    if temp_length_two == 2:
                        #We possibly got both N and M. Or we got (Name: N-)
                        N = int(temp_list_two[0])
                        if temp_list_two[1]:
                            #(Name: N-M)
                            M = int(temp_list_two[1])
                        else:
                            #(Name: N-)
                            M = None
                    elif temp_length_two == 1:
                        #There were no dashes. Thus we get just N.
                        N = int(temp_list_two[0])
                        M = None
                    else:
                        #We got more than one dash. The line wasn't formatted correctly.
                        #We throw an error.
                        raise ValueError("Line: %s has more than one '-'.")
            elif temp_length == 1:
                #We got just a name. The same as (Name:)
                Name = temp_list[0]
                N = 0
                M = None
            else:
                #We got more than one ':'.
                #THIS IS PART OF THE TO DO CASE that has yet to be implemented.
                #It will actually require quite a bit of reworking and factoring.
                #We should make a separate function that parses anything post :
                #Note that there are cases where this can happen.
                #e.g. Anime with names like: Sekai Seifuku: Bouryaku no Zvezda
                #This just further complicates our logic...
                raise ValueError("Line: %s has more than one ':'." % line)
            little_dict = \
                {
                    'folder_name' : Name,
                    'start_num' : N,
                    'end_num' : M
                }
            many_list.append(little_dict)
            num_ranges.append( (N, M) )
    
    return many_list
#Parses the input args. At this point, all we care about is the presence of a file and a bool indicating whether we want to delete or not.
def work_with_file(args):
    """
    Expected format for each line:
    folder_name:start_num-end_num
    This naturally means that you can not have a : in the file name.
    You can still have a "-" in the file_name because the split for that 
    should only happen on the part of the string that follows the colon.
    All spaces on the edges will be stripped but spaces in the middle make no difference.
    If you wish, you may omit the starting number and thus the starting number
    will become the previous line's ending number + 1.
    If there was no previous line, the starting number is 0.
    If you omit the ending number, then all of the remaining images will be moved.
    So, Name:N-M <-All images from N to M (inclusive) will be moved and converted. 
    Name:N <-All images from N to the end will be moved. Same as Name:N-
    Name:-M <-All images from 0 or the earliest possible number to M will be moved.
    Name <-Does all images from beginning to end.
    If an ending number is omitted then the script will perform a check:
    If there is a line after the current one then an error will be thrown.
    We will do this verification later on.
    Empty lines will be ignored and lines beginning with a # will also be ignored.
    If a # is desired at the beginning of the folder name, it must be escaped via a '\'.
    This requirement only applies to a # at the beginning of a folder/end image name not in the middle of one.
    Yes, that means, you can't have comments on a line with data that needs parsing.
    """
    renameHandle = Rename()
    print("Starting run. Moving files from %s to %s " % (renameHandle.screen_path, renameHandle.destination_path) )
    file_name = args[0]
    if len(args) == 2:
        if args[1] == 'd':
            del_old = True
        else:
            raise TypeError("Second argument needs to be d (for deleting old images) or nothing at all.")
    else:
        print('Enter y if you wish to delete the moved images')
        if (input('-> ') == 'y'):
            del_old = True
        else:
            del_old = False
    
    #complete_format = re.compile(r'[\w.\s\-_]+-?\s*:?\s*\d+\s*-?\d+')
    
    many_list = parse_file(file_name)
    
    
    if many_list[-1]['end_num'] is None:
        maxNum = renameHandle.get_max_num(  os.listdir(renameHandle.screen_path)  )
        print (renameHandle.screen_path)
        many_list[-1]['end_num'] = maxNum
    
    rangeWorks = RangeWorks.RangeWorks()
    printDict = PrintDictionary.PrintDictionary()
    do_it = False
    while ( not do_it):
        many_list_fixed = rangeWorks.interpret_ranges_dict(many_list)
        printDict.print_dict(many_list_fixed, rename_format_dict)
        print("Is this okay? Enter y for yes. Enter a to add, r to reload, and n to exit.")
        usr_input = input('-> ')
        if usr_input == 'y':
            do_it = True
        elif usr_input == 'a':
            temp = renameHandle.get_static_input()
            many_list.append(temp)
        elif usr_input == 'n':
            print ("Exiting...")
            break
        elif usr_input == 'r':
            print ("We are going to reload")
            return False
    
    if do_it:
        renameHandle.start_many(many_list_fixed, del_old)
    return True
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        while (not work_with_file(sys.argv[1:])):
            pass
    else:    
        x = Rename()
        x.start()