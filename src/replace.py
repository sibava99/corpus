import glob 
import os.path
import re
exo_type_pat = re.compile(r'(ga|o|ni)="exo." (ga|o|ni)_type="(zero|dep)" ')
noun_exo_pat = re.compile(r'(ga|o|ni)="exo.".?noun')
error_exog = re.compile(r'ga="exog" ga_type="dep"')
sahen_exo = re.compile(r'サ変名詞.*?exo.*?pred')
exo_pat = re.compile(r'(ga|o|ni)="exo." ')
def main():
	pathlist = glob.glob('/home/sibava/corpus/edited_corpus/with_juman_small_excl_exo/dev/*')
	for path in pathlist:
		with open(path,'r',encoding='utf-8') as f:
			s = ''
			s = f.read()
			s = re.sub(exo_type_pat, '', s)
			s = re.sub(exo_pat, '', s)
			# s = re.sub(error_exog,'ga="exog" ga_type="zero"', s)
			# for line in f.readlines():
			# 	line = re.sub(exo_pat, '', line)
			# 	s += line
		with open(path,'w',encoding='utf-8') as f:
			f.write(s)

if __name__ == '__main__':
    main()