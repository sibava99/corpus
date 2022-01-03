import glob 
import os.path
import re
def main():
	juman_ntc_pathlist = glob.glob('/home/sibava/corpus/test_out/active/test/*')
	for juman_path in juman_ntc_pathlist:
		with open(juman_path,'r',encoding='utf-8') as juman:
			s = juman.read()
			if('第一線' in s and '汚染' in s):
				print(juman_path)
				# print(s)

if __name__ == '__main__':
    main()