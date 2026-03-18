import os
import shutil

cmdC = "/Users/danial/Documents/PP2_practices/practice006/copy_demofile.txt"
shutil.copy("/Users/danial/Documents/PP2_practices/practice006/demofile.txt", cmdC)

if os.path.exists(cmdC):
     print("The file was copied successfully.")
else:
     print("The file was not copied.")       

os.remove(cmdC)
if os.path.exists(cmdC):
     print("The file was not deleted.")
else:
     print("The file was deleted successfully.")


