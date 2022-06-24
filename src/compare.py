import glob 
import os.path
import re
def main():
	A_pathlist = glob.glob('/home/sibava/corpus/edited_corpus/with_juman_small_excl_exo/train/*')
	B_pathlist = glob.glob('/home/sibava/corpus/edited_corpus/with_juman_small/train/*')
	A_pathlist.sort()
	B_pathlist.sort()
	for a_path,b_path in zip(A_pathlist,B_pathlist):
		with open(a_path,'r',encoding='utf-8') as a,open(b_path,'r',encoding='utf-8') as b:
			a_lines = a.readlines()
			b_lines = b.readlines()
			if(len(a_lines) != len(b_lines)):
				print(a_path,b_path)
			# for a_line,b_line in zip(a_lines,b_lines):
			# 	if (a_line[0] != b_line[0]):
			# 		print(a_line,b_line)
			# 		print(a_path,b_path)
	


if __name__ == '__main__':
    main()