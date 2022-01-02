import glob
import re
import os
import argparse

id_in_pred_pat = re.compile(r'alt="passive".*?(id="[0-9]*")')
target_pat = re.compile(r'target="(.+?)"')
sid_pat = re.compile(r'sid="(.+?)"')
arg_id_pat = re.compile(r'id="(\d+?)"')
rel_pat = re.compile(r'<rel type="(.+?)"')
id_pat = re.compile(r'id="(\d+?)"')
tag_pat = re.compile(r'<.+?>')
passive_pat = re.compile(r'alt="passive".*')
exo_pat = re.compile(r'\S*?exo.*?zero" ')


success_count = 0
before_zero_count = 0
before_dep_count  = 0
after_zero_count = 0
after_dep_count  = 0
count = 0

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--knp_dir',help='input_knpdir')
    parser.add_argument('--ntc_dir',help='ntc directory with the files corresponding to knp file')
    # ex)python src/refact_change.py --knp_dir KyotoCorpus/dat/rel --ntc_dir sid-juman/dev
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
                        c = -1 #This indicate bunsetsu number
                        sentence_dict[s_id] = []
                    elif(l[0] == '*'):
                        sentence_dict[s_id].append([l])
                        c += 1
                    else:
                        sentence_dict[s_id][c].append(l)
        return sentence_dict

def make_phrase_dict(path_list,encoding_type):
    sentence_dict = {}
    for path in path_list:
        with open(path,'r',encoding=encoding_type) as ntc:
            lines = ntc.readlines()
            s_id = ''
            c = -1
            for l in lines:
                if (l[0] == '#'):
                    s_id = extract_pat(r'# S-ID:(([0-9]|-)*) ', l) #key of sentence_dict (ex.950101004-002)
                    c = -1 #This indicate pharase number
                    sentence_dict[s_id] = []
                elif(l[0] == '*'):
                    continue
                elif(l[0] == '+'):
                    sentence_dict[s_id].append([l])
                    c += 1
                else:
                    sentence_dict[s_id][c].append(l)
    return sentence_dict

def id_search(target:str,arg_id:str,ntc_sentence:str,knp_sentence:str):
    ntc_id = ''
    knp_word_count = 0
    ntc_word_count = 0
    arg_id = int(arg_id)
    for i in range(arg_id + 1):
        tag = knp_sentence[i]
        for morph in tag:
            if(morph[0] == '+'):
                continue
            word = morph.split(' ')[0]
            knp_word_count += len(word)
            if((i == arg_id) and (word == target)):
                break
        else:
            continue
        break

    for bunsetsu in ntc_sentence:
        for morph in bunsetsu:
            if(morph[0]=='*'):
                continue
            ntc_word_count += len(morph.split('\t')[0])
            if((ntc_word_count == knp_word_count) and (ntc_id:=extract_pat(id_pat,morph))):
                return ntc_id
            if(ntc_word_count >= knp_word_count):
                for id_candidate in bunsetsu:
                    match_id = extract_pat(id_pat, id_candidate)
                    if(match_id):
                        ntc_id = match_id
                retval = ntc_id if ntc_id else ''     
                return  retval #return last id in bunsetsu
 
def extract_pat(pat:str,text:str):
    #given pat and text,return pat as str
    target = ''
    m = re.search(pat,text)
    if(m):
        target = m.groups()[0]
    else:
        target = ''
    return target


class pred_info:
    # can't contain duble id in one kaku, use when append niyotte kaku.
    def __init__(self,ga:str='none',ga_type:str='none',o:str='none',o_type:str='none',ni:str='none',ni_type:str='none'):
        self.ga = ga
        self.ga_type = ga_type
        self.o = o
        self.o_type = o_type
        self.ni = ni
        self.ni_type = ni_type
    def has_ids(self):
        ids = [x for x in [self.ga,self.o,self.ni] if not x == 'none']
        return ids
    def find_type(self,target_id):
        type_dict = {}
        type_dict[self.ga] = self.ga_type
        type_dict[self.o] = self.o_type
        type_dict[self.ni] = self.ni_type
        return type_dict[target_id]
    def count_type(self):
        type_list = [self.ga_type,self.o_type,self.ni_type]
        type_freq_dict = {
            'zero':type_list.count('zero'),
            'dep':type_list.count('dep'),
            'none':type_list.count('none')
            }
        return type_freq_dict
    def print_all_info(self):
        print(f'ga={self.ga} type={self.ga_type},o={self.o} type={self.o_type},ni={self.ni} type={self.ni_type}')

def make_ntc_pred_info(pred_tag):
    #for exclude exo
    pred_tag = re.sub(exo_pat, '',pred_tag)

    pred_tag = pred_tag.replace('"','')
    
    tags = pred_tag.split(' ') #ex)[alt="passive" ga="exog" ga_type="zero" o="17" o_type="dep" type="pred"]
    tag_dict = {}
    for tag in tags:
        if not tag.startswith(('ga','o','ni')):
            continue
        key,value = tag.split("=")
        tag_dict[key] = value
    info = pred_info(**tag_dict)
    return info

def search_knp_morph(sid,ntc_word_count,knp_dict):
    tag_info = ''
    knp_word_count = 0
    for knp_bunsetsu in knp_dict[sid]:
        for knp_morph in knp_bunsetsu:
            if(knp_word_count >= ntc_word_count):
                return tag_info
            if(knp_morph[0] == '+'):
                tag_info = knp_morph
                continue
            elif (knp_morph[0] == '*'):
                continue
            else:
                knp_word_count += len(knp_morph.split(' ')[0])
def append_argumentlist(tag,ntc_sentence_dict,knp_tag_dict,kaku,argument_list,ntc_pred_info):
    
    target = extract_pat(target_pat, tag)
    sid = extract_pat(sid_pat, tag)
    arg_id = extract_pat(arg_id_pat, tag)
    ntc_before_ids = ntc_pred_info.has_ids()
    if('不特定' in target):
        if('exog' not in ntc_before_ids):
            return argument_list
        argument_list.append(f'{kaku}="exog"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list
    if(target == '著者'):
        if('exo1' not in ntc_before_ids):
            return argument_list
        argument_list.append(f'{kaku}="exo1"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list   
    if(target == '読者'):
        if('exo2' not in ntc_before_ids):
            return argument_list
        argument_list.append(f'{kaku}="exo2"')
        argument_list.append(f'{kaku}_type="zero"')
        return argument_list
    if not(sid in ntc_sentence_dict):
        return argument_list
    ntc_sentence = ntc_sentence_dict[sid]
    knp_sentence = knp_tag_dict[sid]
    kaku_id = id_search(target, arg_id, ntc_sentence, knp_sentence) 
    if((kaku_id == None) or (len(kaku_id) == 0) or (kaku_id not in ntc_before_ids)):
        return argument_list
    argument_list.append(f'{kaku}="{kaku_id}"')
    argument_list.append(f'{kaku}_type="{ntc_pred_info.find_type(kaku_id)}"')
    return argument_list
     
def make_argumentlist(knp_morph,ntc_sentence_dict,knp_tag_dict,ntc_pred_info):
    tag_list = re.findall(tag_pat,knp_morph)
    argument_list = ['alt="passive"']
    for tag in tag_list:
        rel_type = extract_pat(rel_pat,tag)
        if(rel_type):
            if(rel_type == 'ガ'):
                argument_list = append_argumentlist(tag, ntc_sentence_dict,knp_tag_dict,'ga', argument_list,ntc_pred_info)
            elif(rel_type == 'ニ'or rel_type=='ニヨッテ'):
                argument_list = append_argumentlist(tag, ntc_sentence_dict,knp_tag_dict,'ni', argument_list,ntc_pred_info)
            elif(rel_type == 'ヲ'):
                argument_list = append_argumentlist(tag, ntc_sentence_dict,knp_tag_dict,'o', argument_list,ntc_pred_info)
            # elif(rel_type == 'カラ'):
            #     argument_list = append_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'kara', argument_list,ntc_tag_dict)
            # elif(rel_type == 'デ'):
            #     argument_list = append_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'de', argument_list,ntc_tag_dict)
            # elif(rel_type == 'ガ2'):
            #     argument_list = append_argumentlist(sid, target, arg_id, ntc_dict, knp_tag_dict, 'ga2', argument_list,ntc_tag_dict)
        else:
            pass
    argument_list.append('type="pred"')
    after_pred_info = make_ntc_pred_info(' '.join(argument_list))
    # if(ntc_pred_info.ga == 'exog' and ('exog' not in after_pred_info.has_ids())):


    if(set(ntc_pred_info.has_ids()) == set(after_pred_info.has_ids())):
        global before_zero_count,before_dep_count,after_zero_count,after_dep_count,success_count
        success_count += 1
        ntc_count_dict  = ntc_pred_info.count_type()
        after_count_dict  = after_pred_info.count_type()
        before_zero_count += ntc_count_dict['zero']
        after_zero_count += after_count_dict['zero']
        before_dep_count += ntc_count_dict['dep']
        after_dep_count += after_count_dict['dep']
        print(set(ntc_pred_info.has_ids()),set(after_pred_info.has_ids()))
        ntc_pred_info.print_all_info()
        after_pred_info.print_all_info()
        return argument_list
    else:
        return []

def convert_argument_id(morph,ntc_word_count,sid,ntc_sentence_dict,knp_dict,knp_tag_dict):
    tab_splited_morph = morph.split('\t')
    ntc_pred_info = make_ntc_pred_info(tab_splited_morph.pop())
    knp_morph = search_knp_morph(sid,ntc_word_count,knp_dict)
    argument_list = make_argumentlist(knp_morph,ntc_sentence_dict,knp_tag_dict,ntc_pred_info)
    id_in_pred = extract_pat(id_in_pred_pat, morph)
    if(id_in_pred):
        argument_list.append(id_in_pred)
    joined_argumentlist = ' '.join(argument_list)
    tab_splited_morph.append(joined_argumentlist)
    edited_morph = '\t'.join(tab_splited_morph) + '\n'
    return edited_morph

def convert_passive_file(in_path,active_out_path,passive_out_path,knp_dict,knp_tag_dict):
    ntc_sentence_dict = make_sentence_dict([in_path],'utf-8')
    joined_sentence = ''
    active_joined_sentence = ''
    for k,sentence in ntc_sentence_dict.items():
        ntc_word_count = 0
        if not (k in knp_dict):
            for bunsetsu in sentence:
                for morph in bunsetsu:
                    id_in_pred = extract_pat(id_in_pred_pat,joined_sentence)
                    if(id_in_pred_pat):
                        pred_deleted_morph = re.sub(passive_pat,id_in_pred,morph)
                        joined_sentence += pred_deleted_morph
                        active_joined_sentence += pred_deleted_morph
                    else:
                        pred_deleted_morph = re.sub(passive_pat,'',morph)
                        joined_sentence += pred_deleted_morph
                        active_joined_sentence += pred_deleted_morph
            continue

        for bunsetsu in sentence:
            for morph in bunsetsu:
                if(morph.startswith('*')):
                    joined_sentence += morph
                    active_joined_sentence += morph
                    continue
                ntc_word_count += len(morph.split('\t')[0])
                if ('passive' in morph):
                    edited_morph = convert_argument_id(morph,ntc_word_count,k,ntc_sentence_dict,knp_dict,knp_tag_dict)
                    joined_sentence += edited_morph
                    if('pred' not in edited_morph):
                        active_joined_sentence += edited_morph #failed to correspond to id and delete pred info
                    else:
                        active_joined_sentence += morph # append original morph
                else:    
                    joined_sentence += morph
                    active_joined_sentence += morph
    #for exclude exo
    joined_sentence = re.sub(exo_pat, '', joined_sentence)
    active_joined_sentence = re.sub(exo_pat, '', active_joined_sentence)
    with open(passive_out_path,'w',encoding='utf-8') as passive_out:
        passive_out.write(joined_sentence)
    with open(active_out_path,'w',encoding='utf-8') as active_out:
        active_out.write(active_joined_sentence)



def main():
    parser = create_parser()
    args = parser.parse_args()
    ntc_pathlist = glob.glob(args.ntc_dir + '/*')
    knp_pathlist = glob.glob(args.knp_dir + '/*')
    knp_dict = make_sentence_dict(knp_pathlist,'utf-8')
    knp_tag_dict = make_phrase_dict(knp_pathlist,'utf-8')   

    for path in ntc_pathlist:
        active_out_path = 'test_out/active/test/' + os.path.split(path)[1]
        passive_out_path = 'test_out/passive/test/' + os.path.split(path)[1]
        convert_passive_file(path,active_out_path,passive_out_path,knp_dict,knp_tag_dict)
    print(f'success count {success_count}\nbefore zero count {before_zero_count}\nafter zero count {after_zero_count}\nbefore dep count {before_dep_count}\nafter dep count {after_dep_count}')
if __name__ == '__main__':
    main()