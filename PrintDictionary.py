import copy
import re
from colorama import init, Fore, Back, Style

init(autoreset=True)
default_dict = \
    {
        #We need to dynamically generate this.
        'str_format' : None,
        'in_between' : '\n',
        'colors' : {},
        'count_start' : 0,
        'str.format' : False,
        'default' : [Style.RESET_ALL]
    }

#TO DO:
    #META Colors. <-Highest Priority.
    #Support both in_between_arg and in_between_args at the same time.
    #Add support for a precursor string (print this before the string.)
    #^-Make precursor flexible to just like in between.
#If format dict is not specified, this resorts to using default colors for all the fields.
#By default, the output string would look like this:
# some_key : some_value, some_key : some_value, some_key : some_value, some_key : some_value 
# some_key : some_value, some_key : some_value, some_key : some_value, some_key : some_value
# ...
#It is important to note that the ordering of the keys is arbitrary if str_format is not specified.
#But it will be consistent in between lines just not necessarily in between calls to this function. 
#You can specify a different format using format_dict.
#Possible values for format_dict:
#str_format specifies a string with place holders,
#e.g. " %(some_key)s %(another_key)s BLAH BLAH BLAH %(third_key)s "
#You can also specify a string for in between dict prints. (So the string that goes between the print of two dictionaries)
#By default this is just a standard newline. You can set it some other string.
#You can also use it to specify another format string but you will need to specify a dictionary or a list of dictionaries to use for that formatting.
#A _COUNTER key can be specified in the format string to have the function automatically insert the Count of the Dictionary.
#A _COUNTER key can also be specified in the in_between string BUT it is very important to note that you will require
#an in_between_args if you choose to do so. You can supply an empty one like so:
#format_dict['in_between_args'] : [ {} ] * len(some_dict_col)
#where your in_between string might be " %(_COUNTER)s "
#where some_dict_col is the length of the dictionary collection you wish to print.

#By default count is the same as the index but if you'd rather start it at a different number you may do so with count_start
#start_at_one can be set to True if you'd rather start at 1 for the index. This has no affect if an index is not specified in the format str.
#You can also specify the format of str_format. Namely whether it uses the standard % substitutions or if it uses string.format.
#Templates aren't supported yet.
#Note that instead of using the colors dictionary, you could embed colors straight into str_format if you so wished...
#though that makes me feel like I did all of this work for nothing.
#E.g. 
    # {
        # 'str_format': "%(INDEX)s has this dict (some_key)s %(another_key)s BLAH BLAH BLAH %(third_key)s",
        # 'in_between' : "We have printed a $(type)s dict! \n",
        # 'in_between_args' : [ {'type':'cool' }, { 'type':'cold' }, { 'type':'cool or sort of' }, {  'type':'UNcool'} ],
        # #Alternatively if you'd rather have a constant but runtime generated in_between:
        # #'in_between_arg' : {'type':'cool' },
        # #Note that at the moment you can't use both! It would involve a lot of string replacement and stuff.
        # 'colors' : { \
                        # #Where key_one is a key in some_dict
                        # #Any keys not included will just use the terminal default.
                        # #Note we expect either a list or a single item string. No comma specified strings or anything please!
                        # 'key_one' : [Fore.BLACK,Back.RED,Style.DIM],
                        # 'key_two' : Fore.BLACK
                   # },
        # 'count_start' : 1,
        #
        # #If you wanted this to be true, you'd have specified a str_format like
        # # {INDEX} has this dict {some_key} {another_key} BLAH BLAH BLAH {third_key}
        # 'str.format' : False,
        # #These are static colors for key descriptors and whatever else.
        # #The previous colors thing only colors in the actual values but say you have "name: %(name)s"
        # #and you want name to be colored, well this is what you would use.
        # #Do note that this will still work with the default format string but I wouldn't recommend it...
        # #Also note that for ultimate flexibility you could use Colorama manually.
        # #Note that this will do a search and replace. You don't need to worry about having a weird totally escaped string.
        # #But that also means that you are going to replace any word and not necessarily <- THING MORE ABOUT THIS ONE ZORED.
        # #This will color all words that are not colored otherwise.
        # 'default' : [Fore.BLACK,Back.RED,Style.DIM], 
        # 'meta_colors' : \
            # {
                # #This is going to color all instances of name to Fore.BLACK
                # 'name' : [Fore.BLACK],
                # 'identity' : [Fore.BLACK],
            # },
        # 'meta_ignore_case' : False
    # }
class PrintDictionary(object):
    TOTAL_RESET = Style.RESET_ALL
    SUB_REG = r"%\(\w*\)s"
    
    def __init__(self):
        self.sub_reg = re.compile(self.SUB_REG)
    
    def print_dict(self, some_dict_col, format_dict = None):
        print( self.formatted_dict(some_dict_col, format_dict) )
    
    def get_str_list(self, someThing):
        if isinstance(someThing, str):
            return [ someThing ]
        else:
            #No naughty spaces in our string lists please.
            return [str(x).strip() for x in someThing]
    
    def formatted_dict (self, some_dict_col, format_dict = None):
    
        #Takes a collection of dictionaries (each of which should share the fields to be printed)
        #and returns a nice string as specified by format_dict.
        
        #In theory to make sure we don't actually interfere with the original dictionary, we should make a second collection that is
        #a copy of the original. This is not very efficient...so we won't do it for now...
        #some_dict_col = copy.deepcopy(some_dict_col)
        #(smallest dictionary, largest dictionary)
        extreme_tup = self.get_extreme_dicts(some_dict_col)
        small_dict = extreme_tup[0]
        if format_dict is None:
            format_dict = copy.copy(default_dict)
        else:
            #In case someone wants to call this function multiple times, we want to make sure that we don't touch their version of the format dictionary.
            format_dict = copy.deepcopy(format_dict)
            #We make sure that all of the default values in default_dict are in the user specified format_dict.
            user_format = set(format_dict)
            default_format = set(default_dict)
            if not default_format.issubset(user_format):
                temp_set = default_format - user_format
                for key in temp_set:
                    format_dict[key] = default_dict[key]

        color = format_dict['colors']
        #Make sure everything in the dictionary is a list.
        color = {key : self.get_str_list(color[key]) for key in color}
            
        #We now modify the colors dictionary again and we make sure that each of the keys
        #has at least some value associated with it even if it is just the reset value.
        #but by specifying a default, you get the default instead.
        default_color = self.get_str_list(format_dict['default'])
        #For locality purposes.
        reset_str = self.TOTAL_RESET
        for key in small_dict:
            if key not in color:
                color[key] = default_color
        if '_COUNTER' not in color:
            #We color the COUNTER as well.
            color['_COUNTER'] = default_color

        str_format = format_dict['str_format']
        if not str_format:
            #We need to generate the default format string.
            #We make an assumption here.
            #We assume that the keys to be used are the ones that belong to the smallest dictionary.
            str_format = self.get_default_format_str(some_dict_col, small_dict)

        
        counter = format_dict['count_start']
        #We are going to use a list of in betweens even if they are identical because it will save us some
        #annoying code clutter due to IF/ELSE checks later on.
        if 'in_between_args' in format_dict:
            #We have many arguments for the in between lines.
            #The assumption was made that each dictionary in in_between_args corresponds to one
            #in between.
            in_between_base = format_dict['in_between']
            
            in_bet_temp = []
            for index, temp_dict in enumerate(format_dict['in_between_args']):
                temp_dict['_COUNTER'] = counter
                in_bet_temp.append(in_between_base % temp_dict)
                counter += 1
            in_between_list = in_bet_temp
        elif 'in_between_arg' in format_dict:
            in_between_list = [format_dict['in_between'] %  format_dict['in_between_arg'] ] * len(some_dict_col)
        else:
            in_between_list = [ format_dict['in_between'] ] * len(some_dict_col)
        #We reset counter.
        counter = format_dict['count_start']
        
        dotFormat = format_dict['str.format']
        workList = []
        #I think this is at least N^2. Sob, sob. ;_;
        for index, ourDict in enumerate(some_dict_col):
            some_dict_temp = {'_COUNTER' : ''.join(color['_COUNTER']) +  str(counter) + reset_str}
            for key in ourDict:
                some_dict_temp[key] = ''.join(color[key]) + str(ourDict[key]) + reset_str
            #Gotta get down to business now!
            if dotFormat:
                workList.append(str_format.format(**some_dict_temp) + in_between_list[index])
            else:
                workList.append(str_format % some_dict_temp + in_between_list[index])
            counter += 1
        return ''.join(workList)
    
    # def color_arbitrary_strings(self, to_color, meta_colors, stringFormat = False, default = self.TOTAL_RESET):
        # """
        # This function uses regex to color in stuff. 
        # to_color is the string that needs to be colored.
        # meta_colors is the dictionary that defines which words need to be colored.
        # if default is specified then that is the color all of the strings that are not in meta will take.
        # stringFormat specifies whether we need to be worried about %(key)s or {key} and this is important
        # because we don't want to color the actual "key" in those specifiers.
        # """
        # ret_list = []
        # temp_split_list = to_color.split(' ')
        
    def get_default_format_str(self, dict_col, smallest_dict = None):
        #some_key : some_value, some_key : some_value, some_key : some_value, some_key : some_value
        #First we find the smallest dictionary...
        if smallest_dict is None:
            smallest_dict = self.get_extreme_dicts(dict_col)[0]    
        ret_list = []
        for key in smallest_dict:
            ret_list.append ( "%s : %%(%s)s" % ( key, key ) )
        return ', '.join(ret_list)

    #Gets both the smallest and the largest dictionaries.
    #Returns a tuple: (smallest, largest).
    #Important to note that it doesn't make a copy so modifying either of these will
    #modify the original.
    def get_extreme_dicts(self, dict_col):    
        smallest_dict = dict_col[0]
        largest_dict = dict_col[0]
        for dic in dict_col:
            if len(dic) < len(smallest_dict):
                smallest_dict = dic
            if len(dic) > len(largest_dict):
                largest_dict = dic
        return (smallest_dict, largest_dict)

if __name__ == '__main__':
    x = PrintDictionary()
    temp = [ {'start_num':0, 'end_num':4, 'name':'test' }, {'start_num':3, 'end_num':5, 'name':'test' }, {'start_num':7, 'end_num':9, 'name':'test' } ]
    format_dict = \
        {
            'colors': \
                {
                    'start_num': Fore.GREEN,
                    'end_num' : Fore.RED,
                    'name' : [Fore.BLUE, Back.CYAN, Style.BRIGHT]
                },
            'str_format' : "%(name)s starts at %(start_num)s and ends at %(end_num)s ",
            'in_between' : "%(_COUNTER)s \n",
            'in_between_args' : [ {} ] * len(temp),
            'count_start' : 1,
            'default' : [Fore.YELLOW, Back.BLACK, Style.BRIGHT]
        }
    x.print_dict( temp,   format_dict)
    format_dict['str_format'] = "{name} starts at {start_num} and ends at {end_num} "
    format_dict['str.format'] = True
    x.print_dict( temp,   format_dict)