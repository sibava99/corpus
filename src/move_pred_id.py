import glob 
import os.path
import re
def main():
	juman_ntc_pathlist = glob.glob('/home/sibava/corpus/sid-juman/dev/*')
	pred_id_pat = re.compile(r'alt="passive".*?(id="[0-9]*" )')
	for juman_path in juman_ntc_pathlist:
		with open(juman_path,'r',encoding='utf-8') as juman,open('id-moved-juman/dev/' + os.path.split(juman_path)[1],'w',encoding='utf-8') as moved_juman:
			for l in juman.readlines():
				if(pred_match := re.search(pred_id_pat,l)):
					pred_id = pred_match.groups()[0]
					l = l.replace(pred_id, '')
					tab_splited = l.split('\t')
					tab_splited.insert(-1,pred_id.replace(' ',''))
					l = '\t'.join(tab_splited)
				moved_juman.write(l)

				

if __name__ == '__main__':
    main()