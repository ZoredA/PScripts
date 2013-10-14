import os
import shutil

IMAGEPATH = [r"F:\Photographs"]
OUTPUTPATH=r"E:\temp"
TYPE=("jpg", "jpeg", "png")

class CopyImages:
    #empty dictates if empty directories should be copied or not.
    def __init__(self, IMAGEPATHS, OUTPUTPATH, TYPE = ("jpg", "jpeg", "png"), empty = False):
        if isinstance(IMAGEPATHS, str):
            self.IMAGEPATHS = [IMAGEPATHS]
        else:
            self.IMAGEPATHS = IMAGEPATHS
        if isinstance(OUTPUTPATH, str):
            self.OUTPUTPATH = OUTPUTPATH
        else:
            self.OUTPUTPATH = OUTPUTPATH[0]
        if isinstance(TYPE, str):    
            self.TYPE = (TYPE,)
        else:
            self.TYPE = TYPE
        self.empty = empty
        self.moveFile = self.noReplace
        
    def ignore(self, path, names):
        igList = []
        for name in names:
            namePath = os.path.join(path,name)
            if not os.path.isdir(namePath):
                if not name.lower().endswith( self.TYPE ):
                    igList.append(name)
            else:
                #Don't bother copying empty directories.
                #We also don't bother copying directories that have none of the image types we want.
                #Yes...this is a computationally expensive thing.
                fileList = [fil for fil in os.listdir(namePath) if fil.lower().endswith( self.TYPE )]
                if not fileList and self.empty is False:
                    igList.append(name)
        return igList
        
    #This will copy a directories contents. If the original directory does not
    #exist, it will be created.
    def copyDirCont(self, dirPath):
        r = 0
        #This gets us a file list consisting only of files that end with our specified type.
        fileList = [fil for fil in os.listdir(dirPath) if fil.lower().endswith( self.TYPE )]
        #If our original directory contains no file that we are interested in and we don't wish to create
        #empty directories then we return right now.
        if not fileList and self.empty is False:
            return
        #Gets us something like ('F:', '\\Photographs\\Camping Trip-29 Jun - 2nd Jul 2012\\Raw')
        tempPath = os.path.splitdrive(dirPath)[1].lstrip('\\\\').lstrip('\\')
        outputPath = os.path.join(self.OUTPUTPATH, tempPath)
        if not os.path.isdir(outputPath):
            os.makedirs(outputPath,exist_ok=True)
        for fil in fileList:
            fInputPath = os.path.join(dirPath, fil)
            fOutputPath = os.path.join(outputPath, fil)
            if not os.path.isdir(fInputPath):
                self.moveFile(fInputPath, fOutputPath)
    
    #A function of sorts that will be used to actually move a file.
    #This is dynamically chosen because we might change our mind on whether we want to overwrite files
    #or perhaps overwrite some of them, etc, etc.
    def noReplace(self, filePath, destPath):
        if os.path.exists(destPath):
            return (False, "File %s exists" % filePath)
        shutil.copy2(filePath, destPath)
    
    def myRun(self):
        for curPath in IMAGEPATH:
            for root, dirnames, filenames in os.walk(curPath):
                for dir in dirnames:
                    dirPath = os.path.join(root, dir)
                    self.copyDirCont(dirPath)
                
    def run(self):
        for curPath in IMAGEPATH:
            tempPath = os.path.splitdrive(curPath)[1].lstrip('\\\\').lstrip('\\')
            outputPath = os.path.join(self.OUTPUTPATH, tempPath)            
            if not os.path.exists(outputPath):
                print ( "Directory does not exist. Will use shuttle.copytree" )
                shutil.copytree(curPath, outputPath, ignore = self.ignore)
            else:
                print ("Directory exists will use os.walk.")
                for root, dirnames, filenames in os.walk(curPath):
                    for dir in dirnames:
                        dirPath = os.path.join(root, dir)
                        self.copyDirCont(dirPath)
    
if __name__ == "__main__":
    copyImageObj = CopyImages(IMAGEPATH, OUTPUTPATH, TYPE)
    copyImageObj.run()