import glob
import re
import os
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--knp_dir',help='input_knpdir')
    parser.add_argument('--ntc_dir',help='ntc directory with the files corresponding to knp file')
    # ex)python src/change_passive.py --knp_file KyotoCorpus/dat/rel/950101.knp --ntc_dir NTC_1.5/dat/ntc/knp   
    return parser

def make_sentence_dict(path,encoding_type):
        sentence_dict = {}
        """
        sentence_dict has S-ID as a key and ntc texts as a value.
        
        sentence_dict['# S-ID:950101004-002 KNP:96/10/27 MOD:2004/11/12'] = 
            [
                [* 0 1D,ロシア ろしあ * 名詞 地名 * * eq="1"/id="35",ロシア ろしあ * 名詞 地名 * * eq="1"/id="35",...]
                [* 1 2D,首都 しゅと * 名詞 普通名詞 * * _,グロズヌイ ぐろずぬい * 名詞 地名 * * eq="2"/id="1",に に * 助詞 格助詞 * * _]
                [....]
            ]
        """
        with open(path,'r',encoding=encoding_type) as ntc:
            lines = ntc.readlines()
            s_id = ''
            c = -1
            for l in lines:
                if (l[0] == '#'):
                    s_id = extract_pat(r'# S-ID:(([0-9]|-)*) ', l) #key of sentence_dict (ex. # S-ID:950101004-002 KNP:96/10/27 MOD:2004/11/12)
                    c = -1 #This indicate phrase number
                    sentence_dict[s_id] = []
                elif(l[0] == '*'):
                    sentence_dict[s_id].append([l])
                    c += 1
                else:
                    sentence_dict[s_id][c].append(l)
        return sentence_dict

def make_tag_dict(path):
        sentence_dict = {}
        with open(path,'r',encoding='utf-8') as ntc:
            lines = ntc.readlines()
            s_id = ''
            c = -1
            for l in lines:
                if (l[0] == '#'):
                    s_id = extract_pat(r'# S-ID:(([0-9]|-)*) ', l) #key of sentence_dict (ex.950101004-002)
                    c = -1 #This indicate phrase number
                    sentence_dict[s_id] = []
                elif(l[0] == '*'):
                    continue
                elif(l[0] == '+'):
                    sentence_dict[s_id].append([l])
                    c += 1
                else:
                    sentence_dict[s_id][c].append(l)
        return sentence_dict

def id_search(sid,target,arg_tag,ntc_dict,knp_tag_dict):
    if not (sid in ntc_dict): 
        return ''
    id_pat = r'id="(\d+?)"'
    ntc_id = ''
    word_count = 0
    ntc_word_count = 0
    sentence = knp_tag_dict[sid]
    arg_tag = int(arg_tag)
    for i in range(arg_tag + 1):
        tag = sentence[i]
        for morph in tag:
            if(morph[0] == '+'):
                continue
            word = morph.split(' ')[0]
            word_count += len(word)
            if((i == arg_tag) and (word == target)):
                break
        else:
            continue
        break

    for phrase in ntc_dict[sid]:
        for morph in phrase:
            if(morph[0]=='*'):
                continue
            ntc_word_count += len(morph.split(' ')[0])
            # match_id = extract_pat(id_pat, morph)
            # if(match_id):
            #     ntc_id = match_id
            if((ntc_word_count == word_count) and (morph.split(' ')[0] == target) and (ntc_id:=extract_pat(id_pat,morph))):
                return ntc_id
            if(ntc_word_count >= word_count):
                for id_candidate in phrase:
                    match_id = extract_pat(id_pat, id_candidate)
                    if(match_id):
                        ntc_id = match_id
                retval = ntc_id if ntc_id else ''     
                return  retval #return last id in pharase
    

def extract_pat(pat,text):
    #given pat and text,return pat as str
    target = ''
    m = re.search(pat,text)
    if(m):
        target = m.groups()[0]
    else:
        target = ''
    return target

def make_argumentlist(sid,target,arg_tag,ntc_dict,knp_tag_dict,kaku:str,argument_list):
    unspecified_list = ['不特定:人1','不特定:人2','不特定:人3','不特定:人6','不特定:物1','不特定:物2','不特定:物3','不特定:物4','後文','なし']
    if((target == '不特定:人') or (target == '不特定:状況')):
        argument_list.append(f'{kaku}="exog"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list
    if(target in unspecified_list):

        return argument_list
    if(target == '著者'):
        argument_list.append(f'{kaku}="exo1"')
        argument_list.append(f'{kaku}ga_type="zero"')
        return argument_list   
    if(target == '読者'):
        argument_list.append(f'{kaku}="exo2"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list
    kaku_id = id_search(sid, target, arg_tag, ntc_dict, knp_tag_dict)

    if(len(kaku_id) == 0):
        return argument_list
    argument_list.append(f'{kaku}="{kaku_id}"')
    argument_list.append(f'{kaku}_type="zero"')
    return argument_list

def write_log(sentence_dict:dict,log):
    for k,v in sentence_dict.items():
        log.write(k)
        for phrase in v:
            for morph in phrase:
                log.write(morph)
    return

def main():
    parser = create_parser()
    args = parser.parse_args()
    knp_name = os.path.splitext(os.path.basename(args.knp_dir))
    ntc_pathlist = glob.glob(os.path.join(args.ntc_dir,f'{knp_name[0]}*',))
    knp_pathlist = glob.glob(args.knp_dir + '/*')
    # knp = open(args.knp_dir,'r',encoding='euc-jp')
    # log = open('log_passive_argument.txt',mode = 'w',encoding='euc-jp')
    knp_dict = make_sentence_dict(args.knp_file,'utf-8')
    knp_tag_dict = make_tag_dict(args.knp_file)
    passive_count = 0
    success_count = 0
    gawoni_count = 0
    nini_count = 0
    gani_count = 0
    niwo_count = 0
    gawo_count = 0

    none_knp = 0
    tag_pat = r'<.+?>'
    rel_pat = r'<rel type="(.+?)"'
    target_pat = r'target="(.+?)"'
    sid_pat = r'sid="(.+?)"'
    arg_id_pat = r'id="(\d+?)"'
    for path in pathlist:
        ntc_dict = make_sentence_dict(path,'euc-jp')
        for k,sentence in ntc_dict.items():
            if not (k in knp_dict):
                continue
            ntc_char_num = 0
            for phrase in sentence:
                for morph in phrase:
                    if (morph[0] == '*'):
                        pass
                    else:
                        ntc_char_num += len(morph.split('   ')[0])
                    if ('passive' in morph):
                        knp_char_num = 0
                        passive_morph = morph.split(' ')
                        passive_morph.pop()
                        tag_info = ''
                        for knp_pharase in knp_dict[k]:
                            for knp_morph in knp_pharase:
                                if(ntc_char_num == knp_char_num):
                                    break
                                if (knp_morph[0] == '+'):
                                    tag_info = knp_morph
                                    continue
                                elif (knp_morph[0] == '*'):
                                    continue
                                else:
                                    knp_char_num += len(knp_morph.split(' ')[0])
                            else:
                                continue
                            break
                        # print(tag_info)
                        argument_list = [r'alt="passive"']
                        tag_list = re.findall(tag_pat,tag_info)
                        for tag in tag_list:
                            m = re.match(rel_pat,tag)
                            if(m):
                                target = extract_pat(target_pat, tag)
                                sid = extract_pat(sid_pat, tag)
                                arg_id = extract_pat(arg_id_pat, tag)
                                rel_type = m.groups()[0]
                                if(rel_type == 'ガ'):
                                    argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'ga', argument_list)
                                elif(rel_type == 'ニ'or rel_type=='ニヨッテ'):
                                    argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'ni', argument_list)
                                elif(rel_type == 'ヲ'):
                                    argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'wo', argument_list)
                                elif(rel_type == 'カラ'):
                                    argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'kara', argument_list)
                                elif(rel_type == 'デ'):
                                    argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'de', argument_list)
                                
                            else:
                                pass
                        
                        ntc_id_list = re.findall(r'[0-9]+', morph)
                        # if(exo_ntc := re.search(r'exo.',morph)):
                        #     ntc_id_list.append(exo_ntc.group())
                        knp_id_list = re.findall(r'[0-9]+', ','.join(argument_list))
                        # if(exo_knp := re.search(r'exo.',','.join(argument_list))):
                        #     knp_id_list.append(exo_knp.group())
                        passive_count +=1
                        if (set(knp_id_list) >= set(ntc_id_list)):
                            success_count+=1
                            print(knp_id_list,ntc_id_list)
                            
                            # print(tag_info)
                            # print(argument_list)
                            # print(morph)
                            ga_index = 0
                            wo_index = 0
                            ni_index = 0
                            for arg in argument_list:
                                if ('ga="' in arg):
                                    ga_index +=1
                                if('ni="' in arg):
                                    ni_index +=1
                                if('wo="' in arg):
                                    wo_index +=1
                            if(ni_index >1):
                                nini_count +=1
                                # print(argument_list)     
                                # print(morph)
                                # print(tag_info)
                            if(ga_index >0 and wo_index > 0 and ni_index > 0):
                                gawoni_count +=1
                                
                            if(ga_index>0 and ni_index>0 and wo_index==0):
                                gani_count +=1    
                            if(ga_index>0 and ni_index==0 and wo_index>0):
                                gawo_count +=1
                            if(ga_index==0 and ni_index>0 and wo_index>0):
                                niwo_count +=1 
                                

    
    # knp.close()
    # log.close()

    print(f'identify {passive_count} passive sentence') #Total 1032sentence
    print(f'identify {success_count} of id pair')
    print(f'gani{gani_count},gawo{gawo_count},niwo{niwo_count},nini{nini_count},gawoni{gawoni_count}')
if __name__ == '__main__':
    main()