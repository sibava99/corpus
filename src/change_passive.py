import glob
import re
import os
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--knp_dir',help='input_knpdir')
    parser.add_argument('--ntc_dir',help='ntc directory with the files corresponding to knp file')
    # ex)python src/change_passive.py --knp_dir KyotoCorpus/dat/rel --ntc_dir sid-juman/dev
    return parser

def make_sentence_dict(path_list,encoding_type):
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
        for path in path_list:
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

def make_tag_dict(path_list,encoding_type):
    sentence_dict = {}
    for path in path_list:
        with open(path,'r',encoding=encoding_type) as ntc:
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

def id_search(sid:str,target:str,arg_tag:str,ntc_dict:dict,knp_tag_dict:dict):
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
            ntc_word_count += len(morph.split('\t')[0])
            # match_id = extract_pat(id_pat, morph)
            # if(match_id):
            #     ntc_id = match_id
            if((ntc_word_count == word_count) and (ntc_id:=extract_pat(id_pat,morph))):
                return ntc_id
            if(ntc_word_count >= word_count):
                for id_candidate in phrase:
                    match_id = extract_pat(id_pat, id_candidate)
                    if(match_id):
                        ntc_id = match_id
                retval = ntc_id if ntc_id else ''     
                return  retval #return last id in pharase
    

def extract_pat(pat:str,text:str):
    #given pat and text,return pat as str
    target = ''
    m = re.search(pat,text)
    if(m):
        target = m.groups()[0]
    else:
        target = ''
    return target

def make_argumentlist(sid:str,target:str,arg_tag:str,ntc_dict:dict,knp_tag_dict:dict,kaku:str,argument_list:list,gold_id_list):
    # unspecified_list = ['不特定:人1','不特定:人2','不特定:人3','不特定:人6','不特定:物1','不特定:物2','不特定:物3','不特定:物4','後文','なし']
    # if(target in unspecified_list):
    #     return argument_list
    # if((target == '不特定:人') or (target == '不特定:状況')):
    if('不特定' in target):
        if('exog' not in gold_id_list):
            return argument_list
        argument_list.append(f'{kaku}="exog"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list
    if(target == '著者'):
        if('exo1' not in gold_id_list):
            return argument_list
        argument_list.append(f'{kaku}="exo1"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list   
    if(target == '読者'):
        if('exo2' not in gold_id_list):
            return argument_list
        argument_list.append(f'{kaku}="exo2"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list
    
    kaku_id = id_search(sid, target, arg_tag, ntc_dict, knp_tag_dict) 
    if((kaku_id == None) or (len(kaku_id) == 0) or (kaku_id not in gold_id_list)):
        return argument_list
    argument_list.append(f'{kaku}="{kaku_id}"')
    argument_list.append(f'{kaku}_type="{gold_id_list[kaku_id]}"')
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
    ntc_pathlist = glob.glob(args.ntc_dir + '/*')
    knp_pathlist = glob.glob(args.knp_dir + '/*')
    # knp = open(args.knp_dir,'r',encoding='euc-jp')
    # log = open('log_passive_argument.txt',mode = 'w',encoding='euc-jp')
    knp_dict = make_sentence_dict(knp_pathlist,'utf-8')
    knp_tag_dict = make_tag_dict(knp_pathlist,'utf-8')
    passive_count = 0
    success_count = 0
    gaoni_count = 0
    nini_count = 0
    gani_count = 0
    nio_count = 0
    gao_count = 0
    ga_count = 0
    ni_count = 0
    o_count = 0
    single_count = 0

    none_knp = 0
    tag_pat = re.compile(r'<.+?>')
    rel_pat = re.compile(r'<rel type="(.+?)"')
    target_pat = re.compile(r'target="(.+?)"')
    sid_pat = re.compile(r'sid="(.+?)"')
    arg_id_pat = re.compile(r'id="(\d+?)"')
    passive_pat = re.compile(r'alt="passive".*')
    for path in ntc_pathlist:
        ntc_dict = make_sentence_dict([path],'utf-8')
        with open('passive-juman/train/' + os.path.split(path)[1],'w',encoding='utf-8') as passive_juman:
            for k,sentence in ntc_dict.items(): #fix here!! break and copy sid-juman without sid. delete passive predicat's argument info.
                if not (k in knp_dict):
                    joined = [''.join(x) for x in sentence]
                    passive_juman.write(re.sub(passive_pat,'',''.join(joined)))
                    continue
                ntc_char_num = 0
                for phrase in sentence:
                    for morph in phrase:
                        tab_splited_morph = morph.split('\t')
                        if (morph[0] == '*'):
                            pass
                        else:
                            ntc_char_num += len(tab_splited_morph[0])
                        if ('passive' in morph):
                            passive_count +=1
                            knp_char_num = 0
                            ntc_tag_info = tab_splited_morph.pop() #ex)alt="passive" ga="exog" ga_type="zero" o="17" o_type="dep" type="pred"
                            ntc_tag_dict = {} #ex){'exog': 'zero', '3': 'dep'}
                            for kaku in ['ga','o','ni']:
                                if(search_id := extract_pat(f'{kaku}="(.+?)"', ntc_tag_info)):
                                    ntc_tag_dict[search_id] = extract_pat(f'{kaku}_type="(.+?)"', ntc_tag_info)
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
                                        argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'ga', argument_list,ntc_tag_dict)
                                    elif(rel_type == 'ニ'or rel_type=='ニヨッテ'):
                                        argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'ni', argument_list,ntc_tag_dict)
                                    elif(rel_type == 'ヲ'):
                                        argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'o', argument_list,ntc_tag_dict)
                                    # elif(rel_type == 'カラ'):
                                    #     argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'kara', argument_list,ntc_tag_dict)
                                    # elif(rel_type == 'デ'):
                                    #     argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'de', argument_list,ntc_tag_dict)
                                    # elif(rel_type == 'ガ2'):
                                    #     argument_list = make_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'ga2', argument_list,ntc_tag_dict)
                                else:
                                    pass
                            knp_id_list = re.findall(r'[ga|o|ni|kara|de|ga2]="([0-9]+?)"',','.join(argument_list))
                            if(exo_knp := re.findall(r'exo.',','.join(argument_list))):
                                knp_id_list.extend(exo_knp)
                            # if(set(knp_id_list) != set([x for x in set(ntc_tag_dict.keys()) if x.isdigit()])):
                            if(set(knp_id_list) == set(ntc_tag_dict.keys())):
                            # if(set(knp_id_list) != set(ntc_tag_dict.keys()) and ('exog' in ntc_tag_dict.keys()) and ('exog' not in knp_id_list)):
                                success_count+=1
                                tab_splited_morph.append(' '.join(argument_list + ['type="pred"'])) #if script can make the corresponding,append argumentlist,if not delete predicate informetion and exclude from analysis target
                                # print(knp_id_list,set(ntc_tag_dict.keys()))
                                # print(tag_info)
                                print(argument_list)
                                # print(morph)
                                ga_index = 0
                                o_index = 0
                                ni_index = 0
                                for arg in argument_list:
                                    if ('ga="' in arg):
                                        ga_index +=1
                                    if('ni="' in arg):
                                        ni_index +=1
                                    if('o="' in arg):
                                        o_index +=1
                                # if(len(set(knp_id_list)) == 1):
                                #     single_count += 1
                                if(ni_index >1):
                                    nini_count +=1
                                    # print(argument_list)     
                                    # print(morph)
                                    # print(tag_info)
                                elif(ga_index >0 and o_index > 0 and ni_index > 0):
                                    gaoni_count +=1
                                elif(ga_index>0 and ni_index>0 and o_index==0):
                                    gani_count +=1    
                                elif(ga_index>0 and ni_index==0 and o_index>0):
                                    gao_count +=1
                                elif(ga_index==0 and ni_index>0 and o_index>0):
                                    nio_count +=1 
                                elif(ga_index==1 and ni_index==0 and o_index==0):
                                    ga_count +=1 
                                elif(ga_index==0 and ni_index==1 and o_index==0):
                                    ni_count +=1 
                                elif(ga_index==0 and ni_index==0 and o_index==1):
                                    o_count +=1
                        edited_morph = '\t'.join(tab_splited_morph)
                        if not(edited_morph.endswith('\n')):
                            edited_morph += '\n'
                        passive_juman.write(edited_morph)
    
    # knp.close()
    # log.close()

    print(f'identify {passive_count} passive sentence') #Total 1032sentence
    print(f'identify {success_count} of id pair')
    print(f'ga{ga_count},ni{ni_count},o{o_count},gani{gani_count},gao{gao_count},nio{nio_count},nini{nini_count},gaoni{gaoni_count}')
if __name__ == '__main__':
    main()