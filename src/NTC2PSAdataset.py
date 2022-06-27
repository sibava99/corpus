import glob
import re
import os
import argparse
from pprint import pprint 

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

def extract_psa_info(ntc_text:str) -> dict:
    ntc_text = re.sub('an._id="\d*"', '', ntc_text)
    lines = ntc_text.splitlines()

    preds_info = []
    ids_info = {
        'exog':[{
            'surface_string': 'exog',
            'eq_group': '',
            'sent_index':'-1',
            'arg_indices':[-1]
        }],
        'exo1':[{
            'surface_string': 'exo1',
            'eq_group': '',
            'sent_index':'-1',
            'arg_indices':[-1]
        }],
        'exo2':[{
            'surface_string': 'exo2',
            'eq_group': '',
            'sent_index':'-1',
            'arg_indices':[-1]
        }]
    }   
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
                eq_id = extract_pat(eq_pat,psa_tag)
                arg_indices = [morph_index]
                if(pos == '接尾辞'):
                    surface_string = sentences[sent_index][morph_index - 1] + surface_string
                    arg_indices.insert(0,morph_index - 1)
                if(arg_id  in ids_info):
                    ids_info[arg_id].append(
                        {
                        'surface_string' : surface_string,
                        'eq_group': eq_id,
                        'sent_index':sent_index,
                        'arg_indices':arg_indices
                        }
                    )
                else:
                    ids_info[arg_id] = [{
                        'surface_string' : surface_string,
                        'eq_group': eq_id,
                        'sent_index':sent_index,
                        'arg_indices':arg_indices
                    }]

            morph_index += 1
    return {
        'preds_info':preds_info,
        'ids_info':ids_info,
        'sentences':sentences
    }

def create_goldchain(ids_info:dict)->dict:
    goldchain = {}
    ids_info = [x for x in ids_info.values() if len(x['eq_group'])>0 ]
    for id_info in ids_info:
        eq_id = id_info['eq_group']
        if(eq_id in goldchain):
            goldchain[eq_id].append(id_info['surface_string'])
            print('AAaaaaaaaaaaaas')
        else:
            goldchain[eq_id] = [id_info['surface_string']]
    return goldchain

def calc_abs_index(sentences:list,sent_index:int,index:int)->int:
    abs_index = 0
    for i in range(sent_index):
        abs_index += len(sentences)
    abs_index += index
    return abs_index

def search_nearest_arg(coref_list:list,arg_type:str,pred_sent_index:str,pred_indices:list,sentences:list)->dict:
    pred_index = calc_abs_index(sentences,int(pred_sent_index),int(pred_indices[0]))
    min_pred_distance = 10000
    for arg in coref_list:
        arg_surface,eq_id,arg_sent_index,arg_indices,= arg.values() 
        arg_index = calc_abs_index(sentences,int(arg_sent_index),int(arg_indices[0]))
        if(abs(pred_index - arg_index) < min_pred_distance):
            nearest_arg = arg
            
        if(eq_id == "5"):
            pprint(arg)
        print(arg_index)
    return arg

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    f = open('/home/sibava/corpus/NTC_1.5/dat/ntc/knp/9501ED-0000-950101020.ntc',encoding='euc_jp')
    ntc_text = f.read()
    psa_info = extract_psa_info(ntc_text)
    preds_info = psa_info['preds_info']
    ids_info = psa_info['ids_info']
    sentences = psa_info['sentences']
    # preds_infoを順に回しidのsurfaceをids_infoから取ってくる,共参照の処理,sentencesから述語が登場する文までを文脈として取ってくる
    # eqが同じ形態素にはなぜかidも同じものがふられていた。id_dictを生成し直しこれらを区別する必要がある？
    # 同じidでも距離によって区別し、最も近い物をgold,遠いものをgoldchainとする。この距離は自分で測る
    for pred_info in preds_info:
        pred_surface,pred_type,pred_sent_index,pred_indices,arg_list = pred_info.values()
        for arg in arg_list:
            arg_id,case_type,arg_type = arg.values()
            coref_list = ids_info[arg_id]
            id_info = search_nearest_arg(coref_list,arg_type,pred_sent_index,pred_indices,sentences)


if __name__ == '__main__':
    main()