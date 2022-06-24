import glob
import re
import os
import argparse
import pprint 

id_pat = r'id="(\d*?)"'
eq_pat = r'eq="(\d*?)"'
alt_pat = r'alt="(\w*?)"'
case_pat = r'(\w*?)='
case_id_pat = r'(ga|o|ni)="(\d*?|exo.)"'
arg_type_pat= r'type="(\w*?)"'

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ntc_dir',help='path to NTC')
    # ex)python src/refact_change.py --knp_dir KyotoCorpus/dat/rel --ntc_dir edited_corpus/sid-juman/dev
    return parser

def extract_pat(pat:str,text:str,group:int = 1):
    #given pat and text,return extracted pat as str
    #group indicate the group to be extracted
    m = re.search(pat,text)
    if(m):
        result = m.group(group)
    else:
        result = ''
    return result

def create_arglist(psa_tag:str) -> list:
    arg_list = []
    arg_info = [tag for tag in psa_tag.split('/') if tag.startswith(('ga','o','ni'))]
    while len(arg_info) > 0:
        arg_id = arg_info.pop(0)
        arg_type = arg_info.pop(0)
        case_type = extract_pat(case_pat, arg_id)
        arg_id = extract_pat(case_id_pat,arg_id,2)
        arg_type = extract_pat(arg_type_pat,arg_type)
        arg_list.append({
            'arg_id':arg_id,
            'case_type':case_type,
            'arg_type':arg_type
        })
    return arg_list

def extract_pred_id_info(lines:str) -> dict:
    

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    f = open('/home/sibava/corpus/NTC_1.5/dat/ntc/knp/9501ED-0000-950101020.ntc',encoding='euc_jp')
    lines = f.readlines()

    preds_info = []
    ids_info = {}   # arg_id is key. value
    sentences = [[]]
    sent_index = 0
    morph_index = 0
    for i in range(len(lines)):
        line = lines[i]
        if(line.startswith(('*','#'))):
            pass
        elif(line.startswith('EOS')):
            sent_index +=1
            morph_index = 0
            sentences.append([])
        else:
            surface_string,reading,lemma,pos,grained_pos,conjugate_type,conjugate_form,psa_tag = line.split(' ')
            sentences[sent_index].append(surface_string)
            if('pred' in psa_tag):
                arg_list = []
                pred_indices = [morph_index]
                if((conjugate_type == 'サ変動詞') and ('サ変名詞' in lines[i-1])):
                    sahen_noun = sentences[sent_index][morph_index-1]
                    surface_string = sahen_noun + surface_string
                    pred_indices.insert(0, morph_index-1)
                arg_list = create_arglist(psa_tag)
                preds_info.append(
                    {
                        'surface_string':surface_string,
                        'pred_type':extract_pat(alt_pat,psa_tag),
                        'sent_index':sent_index,
                        'pred_indices':pred_indices,
                        'arg_list':arg_list
                    }
                )

            if('id' in psa_tag):
                arg_id = extract_pat(id_pat,psa_tag)
                eq_id = extract_pat(eq_pat, psa_tag)
                arg_indices = [morph_index]
                if(pos == '接尾辞'):
                    surface_string = sentences[sent_index][morph_index - 1] + surface_string
                    arg_indices.insert(0,morph_index - 1)
                ids_info[arg_id] = {
                    'surface_string' : surface_string,
                    'eq_group': eq_id,
                    'sent_index':sent_index,
                    'arg_indices':arg_indices
                }
            morph_index += 1
    

if __name__ == '__main__':
    main()