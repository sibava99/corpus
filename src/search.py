import glob 
import os.path
import re
def main():
	juman_ntc_pathlist = glob.glob('/home/sibava/corpus/ntc-train-with-juman/test/*')
	for juman_path in juman_ntc_pathlist:
		with open(juman_path,'r',encoding='utf-8') as juman:
			s = juman.read()
			if('拒否'in s and '人種'in s):
				print(juman_path)
				# print(s)
			# lines = juman.readlines()
			# for line in lines:
			# 	if(re.search(r'passive.*?ga="[0-9]+".*?ni="[0-9]+".*?o="[0-9]+".*?',line)):
			# 		print(juman)

if __name__ == '__main__':
    main()