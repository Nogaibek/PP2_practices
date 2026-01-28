

#string in python
str1 = "Hello"
str2 = 'World'
str11 = """Hello World"""
str12 = '''Hello World'''
print(str1)
print(str2)
print(str11)
print(str12)


#Quotes Inside Quotes
str3 = "It's a beautiful day"
str4 = 'He said "Hello" to me'
str8 = 'It\'s a beautiful day'
str9 = "He said \"Hello\" to me"
str10 = "He said \"It's a beautiful day\""
print(str3)
print(str4)
print(str8)
print(str9)
print(str10)


#multple lines string
str5 = """This is a multi-line
string example."""
str6 = '''This is another multi-line
string example.'''
print(str5)
print(str6)    


#Strings are Arrays
str7 = "Hello, World!"
print(str7[0])  #First character
print(str7[7])  #Eighth character
print(str7[-1]) #Last character
print(str7[-5]) #Fifth from last character
print(str7[0:5]) #Substring from index 0 to 4   


#Looping Through a String
for char in str7:
    print(char)


#String Length
print(len(str7))


#Check String
txt = "The best things in life are free!"
print("free" in txt)
print("expensive" not in txt)
print("best" in txt)
print("worst" not in txt)
print("life" in txt)