import glob
import re
import os

def main():
    pathlist = glob.glob('/home/sibava/corpus/NTC_1.5/dat/ntc/ipa/*')
    log = open('passive_file.txt',mode = 'w',encoding='euc-jp')
    for path in pathlist:
        print(f'Loding {path}...')
        with open(path,'r',encoding='euc-jp') as f:
            lines = f.readlines()
            for l in lines:
                if ('passive' in l):
                    log.write(l)
    log.close()

if __name__ == '__main__':
    main()

