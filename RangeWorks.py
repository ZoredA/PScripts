from collections import Counter
from operator import itemgetter
import copy
#TO DO: Alternate, simpler fixer.
#Zig Zags across list.
class RangeError(Exception):
    """An exception we raise when a range has a problem."""
    def __init__(self, start, end, desc = ''):
        self.start = start
        self.end = end
        self.desc = desc
        
    def __str__(self):
        if desc:
            return "Start: %s, End: %s Description: %s" % (self.start, self.end, self.str)
        return "Start: %s, End: %s Description: None" % (self.start, self.end)
        
class RangeMismatchError(Exception):
    """
    An exception thrown when a collection of ranges does not make sense
    and can not be interpreted to make sense.
    e.g. [(0,10), (0,None), (0,None)]
    """
    def __init__(self, index, trouble_col):
        self.index = index
        #Used to decide where to place the arrow!
        temp_arrow = ''
        self.total_fail = False
        try:
            if self.index == 0:
                self.ind_dict = {'ind_one': trouble_col[0], 'ind_two':trouble_col[1], 'ind_three':trouble_col[2]}
                temp_arrow = 'arr_one'
            elif self.index == len(trouble_col) -1 or self.index == -1:
                self.ind_dict = {'ind_one': trouble_col[index - 2], 'ind_two':trouble_col[index - 1], 'ind_three':trouble_col[index]}
                temp_arrow = 'arr_three'
            else:
                self.ind_dict = {'ind_one': trouble_col[index - 1], 'ind_two':trouble_col[index], 'ind_three':trouble_col[index + 1]}
                temp_arrow = 'arr_two'
        except (IndexError, TypeError):
            self.total_fail = True
        else:
            self.ind_dict['arr_one'] = ''
            self.ind_dict['arr_two'] = ''
            self.ind_dict['arr_three'] = ''
            self.ind_dict[temp_arrow] = '<-'
        self.trouble_col = trouble_col
        
    def __str__(self):
        if self.total_fail:
            temp_str = repr(self.trouble_col) + "\n At index: %s" % self.index
        else:
            temp_str = \
            '''
                %(ind_one)s %(arr_one)s
                %(ind_two)s %(arr_two)s
                %(ind_three)s %(arr_three)s
                ''' % self.ind_dict
        return "Range collection can not be interpreted:%sProblem likely at index: %s" % (temp_str, self.index)
        
def comparator(tup):
    return tup[1]

class RangeWorks(object):
    """
    This class does range collision detection and fixing. It is a pretty standard, simple thing.
    Note that this only works for ranges and not arbitrary points.
    Note: This only works for integers at the moment.
    Note: If gaps is set to False, then a range of something like [(0,10), (13-14), (18-19)..]
    will be changed to [(0,10), (11-17), (18-19)]
    """
    def __init__(self, default_start = 0, default_end = None, gaps = True):
        self.default_start = default_start
        self.default_end = default_end
        self.gaps = gaps
        self.sorted = []
        
    #The main worker of our little thing.
    #It wants an iterator of iterators with exactly 2 elements.
    #e.g. [(1,3),(5,7)...]
    #There is no implicit check to make sure that each element has exactly 2 numbers.
    #This is done for the sake of performance.
    #Just so you know.
    def tuple_work(self, tup_col):
        #First we sort em.
        pass
    
    def sort_tup(self, tup_col):
        #Two lists. One sorted by index 0 the other by index 1.
        self.sorted_zero = sorted(tup_col, key=itemgetter(0))
        self.sorted_one = sorted(tup_col, key=itemgetter(1))
    
    #The simplest function. It just checks if there is a range collision or not.
    #If there is one, it returns true, else it returns false.
    #Very inefficient.
    def check_collision(self, tup_col):
        #Set 1 checks for any identical tupples.
        set_one = set(tup_col)
        if len(set_one) != len(tup_col):
            return True;
        
        self.sort_tup(tup_col)
        
        #Set 2 gets just the second values and checks for collisions.
        set_two = set([x[1] for x in self.sorted_zero])
        if len(set_two) != len(tup_col):
            return True;
        
        
        #If the lists are identical, this will return False, else it will return true.
        return self.sorted_zero != self.sorted_one

    #Fixes a list of tuples so that if the first index is exactly one above the previous one
    #if the previous one is equal to self.default_start
    #Expects: [(0,45), (0,66)..]
    #and turns it into [(0,45), (46,66)..]
    def fix_ranges_tup(self, tup_col):
        if len(tup_col) == 1 or not tup_col:
            return tup_col
        new_col = []
        new_col.append(tup_col[0])
        for i in range(1, len(tup_col)):
            if tup_col[i][0] == self.default_start:
                new_col.append(   (tup_col[i-1][1] + 1, tup_col[i][1])   )
            else:
                new_col.append(tup_col[i])
        return new_col
    
    #Same as the previous function but this one works on and returns a dictionary instead.
    #In theory we could get a list of tuples from the dictionary and send it to the other fix ranges to save us some code replication
    #but the code is simple so meh. In theory, fix_ranges_tup could be modified to work in dicts as well but again, that just adds complexity
    #and more checks.
    #By default it does a shallow copy of the original dict but you can specify deepcopy or some other function if you so prefer.
    def fix_ranges_dict(self, dict_col, start_index = 'start_num', end_index = 'end_num', handle = copy.copy):
        if len(dict_col) == 1 or not dict_col:
            return dict_col
        new_col = []
        new_col.append(dict_col[0])
        for i in range(1, len(dict_col)):
            temp = handle(dict_col[i])
            if dict_col[i][start_index] == self.default_start:
                temp[start_index] = dict_col[i-1][end_index] + 1
            new_col.append( temp )
        return new_col        
    
    #A more complex function that automatically tries to interpret missing ranges 
    #and fix them as well as the standard fix the previous two do.
    #If it can't do that, then it throws a RangeMismatchError.
    #Note that by interpret, we mean that it takes a None value in the end_index and
    #tries to match it to the beginning value from the next dict in the collection.
    #E.g [ {0,None}, {45,66}, {0,None}..] will be turned into
    #[ {0,44}, {45,66}, {67,None}]
    #Note that it will leave end_index as None in the last dict BUT if there is one more
    #then it will change that accordingly.
    #TO DO: Think about changing this to be more like the above in terms of how it does the copying.
    #Though to be honest, this might actually be more effeficient but the behaviour is different in that if handle
    #is shallow then this will modify the original dictionary. I guess that is unacceptable.
    def interpret_ranges_dict(self, dict_col, start_index = 'start_num', end_index = 'end_num', handle = copy.copy):
        if len(dict_col) == 1 or not dict_col:
            return dict_col
        new_col = []
        dict_col = handle(dict_col)
        temp_col = [ (x[start_index], x[end_index]) for x in dict_col ]
        temp_final = []
        try:
            temp_final.append(  self.get_interpreted_range(tup_to_check = temp_col[0], tup_before = None, tup_after = temp_col[1])  )
        except RangeMismatchError as e:
            raise RangeMismatchError(0, dict_col)  from e
        for i in range(1, len(dict_col) - 1):
            try:
                temp_final.append(self.get_interpreted_range(temp_col[i], temp_col[i-1], temp_col[i+1]))
            except RangeMismatchError as f:
                #We re-raise the exception but with more useful information.
                raise RangeMismatchError(i, dict_col) from f
            except Exception as genericException:
                #This is mostly for debugging because our exception is much nicer in terms of info presented.
                raise RangeMismatchError(i, dict_col) from genericException
        try:
            temp_final.append(  self.get_interpreted_range(tup_to_check = temp_col[-1], tup_before = temp_col[-2], tup_after = None)  )
        except RangeMismatchError as g:
            g.trouble_col = dict_col
            g.index = -1
            raise RangeMismatchError(-1, dict_col) from g
        for i in range(0, len(dict_col) ):
            temp = handle(dict_col[i])
            temp[start_index] = temp_final[i][0]
            temp[end_index] = temp_final[i][1]
            new_col.append(temp)
        return new_col
        
    #There are a lot of cases to actually check. Not sure if our implementation is bug free.
    #It probably isn't.
    #Returns a tuple with the interpreted range.
    #Since we don't have the complete data structure here we throw a RangeMismatchError if something is wrong. This Exception
    #can then be caught in the calling function and a proper RangeMismatchError can then be thrown.
    #Alternate approach: Simply call quick_after and quick_before and then combine the tuples.
    #It feels like we would be missing some cases if we did that though. Oh well we will do that anyway.
    def get_interpreted_range(self, tup_to_check, tup_before, tup_after):
        if tup_to_check[0] !=  self.default_end and tup_to_check[1] !=  self.default_end:
            if tup_to_check[0] > tup_to_check[1]:
                #Can't be bothered to check if before and after are None are not so we just send empty tuples.
                #This will happen if we get a tup like (3,2)
                raise RangeMismatchError(1, [(), tup_to_check, ()])
        if not tup_before: 
            if not tup_after: 
                #No tuple came before and none after so it is likely a single element collection.
                return tup_to_check
            return self.quick_after(tup_to_check, tup_after)
        elif not tup_after:
            return self.quick_before(tup_to_check, tup_before)
        
        tup_to_check = self.quick_before(tup_to_check, tup_before)
        tup_to_check = self.quick_after(tup_to_check, tup_after)
        return tup_to_check
                
    def quick_before(self, tup_to_check, tup_before):
        if tup_to_check[0] == self.default_start:
            if tup_before[1] == self.default_end:
                raise RangeMismatchError(1, [tup_before, tup_to_check, ()])
            return (tup_before[1] + 1, tup_to_check[1])
        elif tup_before[1] != self.default_end:
            if tup_to_check[0] < tup_before[1]:
                raise RangeMismatchError(1, [tup_before, tup_to_check, ()])
            if self.gaps or tup_to_check[0] == tup_before[1] + 1:
                return tup_to_check
            return (tup_before[1] + 1, tup_to_check[1])
        else:
            #This tuple is valid but the next one has a default start value.
            return tup_to_check            

    def quick_after(self, tup_to_check, tup_after):
        if tup_to_check[1] == self.default_end:
            if tup_after[0] == self.default_start:
                raise RangeMismatchError(1, [(), tup_to_check, tup_after])
            return (tup_to_check[0], tup_after[0] - 1)
        elif tup_after[0] != self.default_start:
            if tup_to_check[1] > tup_after[0]:
                raise RangeMismatchError(1, [(), tup_to_check, tup_after])
            if self.gaps or tup_to_check[1] == tup_after[0] - 1:
                return tup_to_check
            return (tup_to_check[0], tup_after[0] - 1)
        else:
            #This tuple is valid but the next one has a default start value.
            return tup_to_check

def verify(col, in_key_start = 0, in_key_end = 1):
    for index, item in enumerate(col):
        if index == 0: continue
        try:
            prev = col[index - 1]
            if not item[in_key_start] > prev[in_key_end]:
                raise RangeMismatchError(index, col)
            next = col[index + 1]
            if not next[in_key_start] > item[in_key_end]:
                raise RangeMismatchError(index, col)           
        except IndexError:
            return True
    return True
    
if __name__ == '__main__':
    try:
        import random
        x = RangeWorks()
        #Single Element tests
        #Two Element tests
        s_tup = x.fix_ranges_tup( [ (0,10) ] )
        s_tup = x.fix_ranges_tup( [ (0,None) ] )
        s_tup = x.fix_ranges_tup( [ (3,10) ] )
        print(str(s_tup) + " <- Single Tup" )
        
        s_dict = x.fix_ranges_dict( [ {'start_num':0, 'end_num':4, 'name':'test' } ] )
        s_dict = x.fix_ranges_dict( [ {'start_num':0, 'end_num':None, 'name':'test' } ] )
        s_dict = x.fix_ranges_dict( [ {'start_num':3, 'end_num':10, 'name':'test' } ] )
        
        print(str(s_dict) + " <- Single Dict" )
        
        s_dict = x.interpret_ranges_dict( [ {'start_num':0, 'end_num':4, 'name':'test' } ] )
        s_dict = x.interpret_ranges_dict( [ {'start_num':0, 'end_num':None, 'name':'test' } ] )
        s_dict = x.interpret_ranges_dict( [ {'start_num':3, 'end_num':10, 'name':'test' } ] )
        
        print(str(s_dict) + " <- Single Dict Interpreted" )        
        
        #Manual Tests
        
        try:
            s_dict = x.interpret_ranges_dict( [ {'start_num':0, 'end_num':4, 'name':'test' }, {'start_num':3, 'end_num':5, 'name':'test' }, {'start_num':7, 'end_num':9, 'name':'test' } ] )
        except Exception as f:
            print(f)
        try:
            s_dict = x.interpret_ranges_dict( [ {'start_num':0, 'end_num':4, 'name':'test' }, {'start_num':5, 'end_num':9, 'name':'test' }, {'start_num':7, 'end_num':8, 'name':'test' } ] )
        except Exception as f:
            print(f)
        try:
            s_dict = x.interpret_ranges_dict( [ {'start_num':0, 'end_num':None, 'name':'test' }, {'start_num':0, 'end_num':5, 'name':'test' }, {'start_num':7, 'end_num':8, 'name':'test' } ] )
        except Exception as f:
            print(f)
            
        print(str(s_dict) + " <- Single Dict Interpreted" )       
        to_test_tups = []
        to_test_dict = []
        to_test_rand_fail_dict = []
        for i in range(0,10000):
            num = random.randint(1,15)
            if num % 2 == 0:
                num_two = random.randint(1,7)
                if num_two == 1:
                    to_test_rand_fail_dict.append ( {'start_num':0, 'end_num':i, 'name':'test' } )
                elif num_two == 2:
                    to_test_rand_fail_dict.append ( {'start_num':0, 'end_num':None, 'name':'test' } )
                else:
                    to_test_rand_fail_dict.append ( {'start_num':0, 'end_num':i, 'name':'test' } )
                # elif num_two == 3:
                    # to_test_rand_fail_dict.append ( {'start_num':i, 'end_num':i, 'name':'test' } )
                # else:
                    # to_test_rand_fail_dict.append ( {'start_num':i, 'end_num':None, 'name':'test' } )
            if num % 3 == 0:
                to_test_tups.append( (0,i) )
            if num % 4 == 0:
                to_test_dict.append ( {'start_num':0, 'end_num':i, 'name':'test' } )
                
        print (len(to_test_tups))
        print (to_test_tups[-1])
        print (len(to_test_dict))
        print (to_test_dict[-1])
        
        fixed_tup = x.fix_ranges_tup(to_test_tups)
        print('Fixed tup')
        print (len(fixed_tup))
        print (fixed_tup[-1], fixed_tup[-2])
        verify(fixed_tup)
        
        print('Checking tup collision')
        print('Collision is now %s and it used to be %s' % (x.check_collision(fixed_tup), x.check_collision(to_test_tups)) )

        fixed_dict = x.fix_ranges_dict(to_test_dict)
        print('Fixed dict')
        print (len(fixed_dict))
        print (fixed_dict[-1], fixed_dict[-2])
        verify(fixed_dict, 'start_num', 'end_num')
        
        fixed_dict = x.interpret_ranges_dict(to_test_dict)
        print('Fixed dict with interpret')
        print (len(fixed_dict))
        print (fixed_dict[-1], fixed_dict[-2])
        verify(fixed_dict, 'start_num', 'end_num')
        
        try:
            weirdo = x.interpret_ranges_dict(to_test_rand_fail_dict)
        except RangeMismatchError as e:
            print("Weirdo is obviously weird")
            print(e)
        else:
            verify(weirdo, 'start_num', 'end_num')
            print("Weirdo seems okay...")
    except RangeMismatchError as e:
        print (e)
        raise