import json
import glob
import re
import os.path
import pandas as pd

def main():	

	a_path = '/home/sibava/ZAR-konno/data/with_juman_small_b/cl-tohoku-bert.train.instance.jsonl'
	b_path = '/home/sibava/ZAR-konno/data/with_juman_small_excl_exo_b/cl-tohoku-bert.train.instance.jsonl'

	a_df = pd.read_json(a_path,lines=True)
	b_df = pd.read_json(b_path,lines=True)

	l_count = 0
	for a_tokens,b_tokens in zip(a_df['input_tokens'],b_df['input_tokens']):
		if(a_tokens != b_tokens):
			print(a_tokens)
			print(l_count)
			exit(0)
		l_count += 1
if __name__ == '__main__':
    main()