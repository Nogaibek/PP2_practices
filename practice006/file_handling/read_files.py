f = open("/Users/danial/Documents/PP2_practices/practice006/demofile.txt", "r")
print(f.read())
f.close()

with open("/Users/danial/Documents/PP2_practices/practice006/demofile.txt", "r") as f:
    print(f.read())
