import glob
import re
import os
import argparse
from pprint import pprint 
from typing import List, Tuple, Dict, Set,TypedDict
import json
from tqdm import tqdm

id_pat = r'id="(\d*?)"'
eq_pat = r'eq="(\d*?)"'
alt_pat = r'alt="(\w*?)"'
case_pat = r'(\w*?)='
case_id_pat = r'(ga|o|ni)="(\d*?|exo.)"'
case_id_pat = r'="(\d*?|exo.)"'
arg_type_pat= r'_type="(\w*?)"'

class Arg(TypedDict):
    """
    述語がもつ項の情報を表す
    
    * arg_id : NTCにおいて与えられたid
    * case_type : 格の種類　[が,を,に]
    * arg_type : 述語と項の間の関係 [dep or zero]
    """
    arg_id:str
    case_type:str
    arg_type:str

class IdMorph(TypedDict):
    """
    ガ格，ヲ格，ニ格の格要素となりうる表現の情報

    * surface_string : 形態素の出現系
    * eq_group : 共参照グループ。この値が同じ形態素は共参照関係にある
    * sent_index : 形態素が出現する文番号
    * morph_indices : 形態素が出現する文中の位置。形態素が[佐藤,さん]のように分離されているときは[29,30]のようになる
    """

    surface_string:str
    eq_group:str
    sent_index:int
    morph_indices:list[int]

class Pred(TypedDict):
    surface_string:str
    alt_type:str
    sent_index:int
    pred_indices:List[int]
    arg_list:List[IdMorph]


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ntc_dir',help='path to NTC')
    parser.add_argument('--output_path',help='output path')
    return parser

def extract_pat(pat:str,text:str,group:int = 1)->str:
    #given pat and text,return extracted pat as str
    #group indicate the group to be extracted
    m = re.search(pat,text)
    if(m):
        result = m.group(group)
    else:
        result = ''
    return result

def _concat_arg(lines,line_index,morph_index,surface_string,morph_indices):
    surface_string = lines[line_index].split()[0] + surface_string
    morph_indices.insert(0,morph_index)
    previous_line = lines[line_index - 1]
    if('接尾辞' in lines[line_index]):
        surface_string,morph_indices = _concat_arg(lines, line_index -1 , morph_index -1, surface_string, morph_indices)
    return surface_string,morph_indices

def create_arglist(psa_tag:str) -> list[Arg]:
    arg_list = []
    arg_info = [tag for tag in psa_tag.split('/') if tag.startswith(('ga','o','ni'))]
    while len(arg_info) > 0:
        arg_id = arg_info.pop(0)
        arg_type = arg_info.pop(0)
        
        case_type = extract_pat(case_pat, arg_id)
        arg_id = extract_pat(case_id_pat,arg_id,2)
        arg_type = extract_pat(arg_type_pat,arg_type)
        arg:Arg = {
            'arg_id':arg_id,
            'case_type':case_type,
            'arg_type':arg_type
        }
        arg_list.append(arg)
    return arg_list

def new_create_arglist(psa_tag:str) -> list[Arg]:
    arg_list = []
    for case in ['ga','o','ni']:
        arg_id = extract_pat(case + case_id_pat,psa_tag)
        arg_type = extract_pat(case + arg_type_pat,psa_tag)
        if(arg_id == '' and arg_type == ''):
            arg_id = 'none'
            arg_type = 'none'
        arg:Arg = {
            'arg_id':arg_id,
            'case_type':case,
            'arg_type':arg_type
        }
        arg_list.append(arg)
    return arg_list

def extract_psa_info(ntc_text:str) -> dict:
    ntc_text = re.sub('an._id="\d*"', '', ntc_text)
    lines = ntc_text.splitlines()

    exog:IdMoprh = {
            'surface_string': 'exog',
            'eq_group': '',
            'sent_index':'-1',
            'morph_indices':[-1]
        }
    exo1:IdMorph = {
            'surface_string': 'exo1',
            'eq_group': '',
            'sent_index':'-1',
            'morph_indices':[-1]
        }
    exo2:IdMorph = {
            'surface_string': 'exo2',
            'eq_group': '',
            'sent_index':'-1',
            'morph_indices':[-1]
        }
    none:IdMorph = {
            'surface_string': 'none',
            'eq_group': '',
            'sent_index':'-1',
            'morph_indices':[-1]
        }

    idmorphs = {
        'exog':[exog],
        'exo1':[exo1],
        'exo2':[exo2],
        'none':[none]
    } 

    sentences = [[]]
    sent_index = 0
    morph_index = 0
    preds = []
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
                arg_list = new_create_arglist(psa_tag)
                pred:Pred ={
                        'surface_string':surface_string,
                        'alt_type':extract_pat(alt_pat,psa_tag),
                        'sent_index':sent_index,
                        'pred_indices':pred_indices,
                        'arg_list':arg_list,
                    }
                preds.append(pred)


            if('id' in psa_tag):
                arg_id = extract_pat(id_pat,psa_tag)
                eq_id = extract_pat(eq_pat,psa_tag)
                # morph_indices = [morph_index]
                # if(pos == '接尾辞'):
                #     previus_line = lines[i-1]
                #     surface_string = sentences[sent_index][morph_index - 1] + surface_string
                #     morph_indices.insert(0,morph_index - 1)
                surface_string,morph_indices = _concat_arg(lines=lines,line_index= i,morph_index=morph_index,surface_string='',morph_indices=[])
                idmorph:IdMorph = {
                        'surface_string' : surface_string,
                        'eq_group': eq_id,
                        'sent_index':sent_index,
                        'morph_indices':morph_indices
                }
                if(arg_id  in idmorphs):
                    idmorphs[arg_id].append(
                        idmorph
                    )
                else:
                    idmorphs[arg_id] = [
                        idmorph
                    ]

            morph_index += 1
    return {
        'preds':preds,
        'idmorphs':idmorphs,
        'sentences':sentences
    }

def create_goldchains(idmorphs:dict)->dict:
    goldchains = {}
    for arg_id,coref_list in idmorphs.items():
        goldchain = []
        for arg in coref_list:
            goldchain.append(arg['surface_string'])
        goldchain = list(set(goldchain))
        goldchains[arg_id] = goldchain
    return goldchains

def calc_abs_index(sentences:list,sent_index:int,index:int)->int:
    abs_index = 0
    for i in range(sent_index):
        abs_index += len(sentences)
    abs_index += index
    return abs_index

def search_nearest_arg(coref_list:list,pred_sent_index:str,pred_indices:list,sentences:list)->IdMorph:
    pred_index = calc_abs_index(sentences,int(pred_sent_index),int(pred_indices[0]))
    min_pred_distance = 10000
    for arg in coref_list:
        arg_surface,eq_id,arg_sent_index,morph_indices,= arg.values() 
        arg_index = calc_abs_index(sentences,int(arg_sent_index),int(morph_indices[0]))
        if(abs(pred_index - arg_index) < min_pred_distance):
            min_pred_distance = abs(pred_index - arg_index)
            nearest_arg = arg
    return nearest_arg

def determin_argtype(pred:Pred,idmorph:IdMorph,arg_type:str)->str:
    if(arg_type == 'dep'):
        return 'dep'
    elif(arg_type == 'none'):
        return 'none'
    elif(idmorph['surface_string'].startswith('exo')):
        return idmorph['surface_string'] #exog,exo1,exo2
    elif(pred['sent_index'] == idmorph['sent_index']):
        return 'intra'
    else:
        return 'inter' 

def main():
    parser = create_parser()
    args = parser.parse_args()
    ntc_dir = args.ntc_dir
    output_path = args.output_path

    if os.path.exists(ntc_dir):
        print(f"Loading {ntc_dir}")
    else:
        print("NTC path does not exist")

    # ntc_paths = glob.glob(os.path.join(ntc_dir,'dat/ntc/knp/*'))
    ntc_paths = glob.glob(os.path.join(ntc_dir,'*'))
    output_file = open(os.path.join(output_path,'psat5instance.test.jsonl'),encoding='utf-8',mode='w')
    print(len(ntc_paths)) 
    for ntc_path in tqdm(ntc_paths):
        with open(ntc_path,encoding='euc_jp',mode='r') as f:
            ntc_text = f.read()
        psa_info = extract_psa_info(ntc_text)
        preds = psa_info['preds']
        idmorphs = psa_info['idmorphs']
        sentences = psa_info['sentences']
        # predsを順に回しidのsurfaceをidmorphsから取ってくる,共参照の処理,sentencesから述語が登場する文までを文脈として取ってくる
        # eqが同じ形態素にはなぜかidも同じものがふられていた。id_dictを生成し直しこれらを区別する必要がある？
        # 同じidでも距離によって区別し、最も近い物をgold,遠いものをgoldchainとする。この距離は自分で測る
        goldchains = create_goldchains(idmorphs=idmorphs)
        for pred in preds:
            context = sentences[:pred["sent_index"]+1]
            for arg in pred["arg_list"]:
                coref_list = idmorphs[arg['arg_id']]
                nearlest_idmorph = search_nearest_arg(coref_list,pred['sent_index'],pred['pred_indices'],sentences)
                arg_type = determin_argtype(pred,nearlest_idmorph,arg['arg_type'])
                goldchain = goldchains[arg['arg_id']]
                psa_instance = {
                    'context':context,
                    'pred_surface':pred['surface_string'],
                    'alt_type':pred['alt_type'],
                    'pred_sent_index':pred['sent_index'],
                    'pred_indices':pred['pred_indices'],
                    'case_type':arg['case_type'],
                    'arg_type':arg_type,
                    'arg_surface':nearlest_idmorph['surface_string'],
                    'arg_sent_index':nearlest_idmorph['morph_indices'],
                    'arg_indices':nearlest_idmorph['morph_indices'],
                    'goldchain':goldchain,
                    'ntc_path':ntc_path
                }
                output_file.write(json.dumps(psa_instance) + '\n')
    output_file.close()
    
if __name__ == '__main__':
    main()