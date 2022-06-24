import glob 
import os.path

def main():
	juman_ntc_pathlist = glob.glob('/home/sibava/corpus/edited_corpus/with_juman_small_excl_exo/dev/*')
	juman_tail_path = [os.path.split(x)[1] for x in juman_ntc_pathlist]
	original_ntc_pathlist = glob.glob('/home/sibava/corpus/NTC_1.5/dat/ntc/ipa/*')
	original_ntc_pathlist = [x for x in original_ntc_pathlist if(os.path.split(x)[1] in juman_tail_path)]
	juman_ntc_pathlist.sort()
	original_ntc_pathlist.sort()
	for juman_path,original_path in zip(juman_ntc_pathlist,original_ntc_pathlist):
		with open(juman_path,'r',encoding='utf-8') as juman,open(original_path,'r',encoding='euc-jp') as original,open('/home/sibava/corpus/edited_corpus/sid_juman_small_excl_exo/dev/'+os.path.split(juman_path)[1],'w',encoding='utf-8') as new_juman:
			sid_list = [x for x in original.readlines() if x.startswith('#')][::-1]
			new_juman.write(sid_list.pop())
			for line in juman.readlines():
				new_juman.write(line)
				if(line.startswith('EOS') and len(sid_list)>0):
					new_juman.write(sid_list.pop())

if __name__ == '__main__':
    main()