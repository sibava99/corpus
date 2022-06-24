import glob
import re
import os
import argparse
import random

def create_parser():
	#python src/dataset_split.py --original edited_corpus/remix_mapped_excl_exo_small/passive/tmp --random --out_dir edited_corpus/remix_mapped_excl_exo_small/passive 
    parser = argparse.ArgumentParser()
    parser.add_argument('--original',help='original dataset')
    parser.add_argument('--random',help='random split',action='store_true')
    parser.add_argument('--out_dir',help='output dir path')
	
    return parser

def main():
	parser = create_parser()
	args = parser.parse_args()
	out_path = args.out_dir
	pathlist = glob.glob(args.original + '/*')
	if(args.random):
		random.Random(2022).shuffle(pathlist)
	train_set = pathlist[:int(len(pathlist)*0.7)]
	devtest_set = pathlist[int(len(pathlist)*0.7):]
	dev_set = devtest_set[:int(len(devtest_set)*0.666)]
	test_set = devtest_set[int(len(devtest_set)*0.666):]	
	assert len(pathlist) == (len(train_set) + len(dev_set) + len(test_set)),'not equal the number of data'
	
	
	for path in train_set:
		with open(path,'r') as f:
			s = f.read()
		with open(os.path.join(out_path,'train',os.path.basename(path)),'w') as f:
			f.write(s)
	for path in test_set:
		with open(path,'r') as f:
			s = f.read()
		with open(os.path.join(out_path,'test',os.path.basename(path)),'w') as f:
			f.write(s)	
	for path in dev_set:
		with open(path,'r') as f:
			s = f.read()
		with open(os.path.join(out_path,'dev',os.path.basename(path)),'w') as f:
			f.write(s)

if __name__ == '__main__':
    main()