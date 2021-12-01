import glob
import re
import os
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--knp_dir',help='input_knpdir')
    parser.add_argument('--ntc_dir',help='ntc directory with the files corresponding to knp file')
    # ex)python src/change_passive.py --knp_dir KyotoCorpus/dat/rel/950101.knp --ntc_dir NTC_1.5/dat/ntc/ipa
    return parser

def extract_pat(pat:str,text:str):
    #given pat and text,return pat as str
    target = ''
    m = re.search(pat,text)
    if(m):
        target = m.groups()[0]
    else:
        target = ''
    return target

def make_doc_dict(path_list,encoding_type):
	"""
	doc_dict contain all sentences in the document with keys which indeces the number of sentence.
	doc_dict['950101004-001] = 
            [
                [* 0 1D,ロシア ろしあ * 名詞 地名 * * eq="1"/id="35",ロシア ろしあ * 名詞 地名 * * eq="1"/id="35",...]
                [* 1 2D,首都 しゅと * 名詞 普通名詞 * * _,グロズヌイ ぐろずぬい * 名詞 地名 * * eq="2"/id="1",に に * 助詞 格助詞 * * _]
                [....]
            ]
	"""
	for path in path_list:
		with open(path,'r',encoding=encoding_type) as doc:
			lines = doc.readlines()
			sentence_count = 0
			c = -1
			for l in lines:
				


def main():
	parser = create_parser()
	args = parser.parse_args()
	ntc_pathlist = glob.glob(args.ntc_dir + '/9501*')
	knp_pathlist = glob.glob(args.knp_dir + '/*')



if __name__ == '__main__':
    main()