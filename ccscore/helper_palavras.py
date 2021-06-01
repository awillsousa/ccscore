# Create data strucutures with PALAVRAS tags and
# provide functions for parsing and processing

from palavras_dic_tags import SEMANTIC_TAGSET
from palavras_dic_tags import *
from bs4 import BeautifulSoup
import split_utils as su
import requests
from enum import Enum

class TypeTagset(Enum):
    WORD_CLASS = 'WORD_CLASS'
    WORD_SUBCLASS = 'WORD_SUBCLASS'
    INFLEXION = 'INFLEXION'
    SYNTATIC = 'SYNTATIC'
    TEXT_METAINFO = 'TEXT_METAINFO'
    SEMANTIC = 'SEMANTIC'
    NOMINAL_VALENCY = 'NOMINAL_VALENCY'
    VERBAL_VALENCY = 'VERBAL_VALENCY'
    ALL = 'ALL'


class TokenVISL(object):    
    def __init__(self, pos, text, lemma, tags, ref=None):
        self.pos = pos
        self.text = text
        self.lemma = lemma
        self.tags = tags
        self.ref = ref

    def __str__(self):
        return f"{self.text} {self.tags}"

    def __repr__(self):
        return f"{self.text}"

    def get_tags(self, type_tag=TypeTagset.ALL):
        if type_tag == TypeTagset.ALL:
            return self.tags
        else:
            return [x for x in self.tags if x[1] == type_tag]

class SentenceVISL(object):
    def __init__(self, pos, tokens, text):
        self._index = 0
        self.pos = pos
        self.tokens = tokens
        self.text = text
    
    def __str__(self):
        return f"{self.text}"
    
    def __getitem__(self, n):
        if n < len(self.tokens):
            return self.tokens[n]
        else:
            raise IndexError("Indice de token fora do intervalo.")

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self.tokens):
            raise StopIteration

        r = self.tokens[self._index]
        self._index += 1
        return r


class DocVISL(object):
    def __init__(self, sentences):
        self._index = 0
        self.sentences = sentences

    def __getitem__(self, pos):
        return self.sentences[pos]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self.sentences):
            raise StopIteration

        r = self.sentences[self._index]
        self._index += 1
        return r


def is_umbrella(tag):
    """
    Return true if 'tag' is an semantic umbrella tag
    """

    if tag in SEMANTIC_TAGSET.keys():
        return SEMANTIC_TAGSET[tag]['umbrella']

    return False


def identify_tag(tag):
    '''
    Help to identify the tag passed using dictionaries based on
    PALAVRAS rules    
    '''
    TAGSETS = [WORD_CLASS_TAGSET, WORD_SUBCLASS_TAGSET, INFLEXION_TAGSET, 
               SYNTATIC_TAGSET, TEXT_METAINFO_TAGSET, SEMANTIC_TAGSET, 
               NOMINAL_VALENCY_TAGSET, VERBAL_VALENCY_TAGSET]
    IDS_TAGSETS = ['WORD_CLASS', 'WORD_SUBCLASS', 'INFLEXION', 
                   'SYNTATIC', 'TEXT_METAINFO', 'SEMANTIC',
                   'NOMINAL_VALENCY', 'VERBAL_VALENCY']
    
    for name_ts, ts in zip(IDS_TAGSETS,TAGSETS):        
        if tag in ts.keys():
            return name_ts
        
    return "UNKNOWN"


MARK_START_SENTENCE = "<ß>"
MARK_END_SENTENCE = "</ß>"
# Punctuation that not break sentence
PUNCT_CONTIN = [": ", "; "]
TOKEN_PUNCT = [",", ":", "\"", "?", "!"]

def is_token_punct(t):
    return t in TOKEN_PUNCT


def process_line(linha):
    '''
    Receive one line of text with PALAVRAS
    tags and convert to a tuple
    t = (token, original_token_form, [tags of token], reference)
    token - it's the word exact like in text, except for words
            like "do" that are preposition+article and are split up
            in two parts
    token_original_form - it's result of lemmatization of token
    [tags of token] - list of tags of PALAVRAS
    reference - a text string with the format (#N -> M), with 
                the dependency reference
    '''
    token_1 = token_2 = token_3 = ""
        
    part_linha = linha.split('[')

    if len(part_linha) > 0:
        token_1 = part_linha[0].strip()

    part_linha = part_linha[1].split(']')
    token_2 = part_linha[0]
    #tags_linha = [ t for t in part_linha[1].split(' ') if t != '' and MARK_END_SENTENCE not in t]
    
    tags_linha = []
    ref = ""
    for t in part_linha[1].split(' '):
        if "#" in t and "->" in t:
            ref = t    
        elif t != '' and MARK_END_SENTENCE not in t:
            tags_linha.append((t, identify_tag(t)))
            
    return (token_1, token_2, tags_linha, ref)


def parse_file_toclass(filepath, original_text):
    '''
    Parse line by line a file with PALAVRAS
    tags, stored with html tags
    '''
    orig_sentences = []
    try:
        with open(original_text, 'r') as f_text:
            orig_sentences = su.split_by_sentence("\n".join(f_text.readlines()))
    except IOError:
        print(f"Erro ao tentar abrir o arquivo {original_text}")

    html_lines = []
    try:
        with open(filepath, 'r') as f_html:
            html_lines = f_html.readlines()
    except IOError:
        print(f"Erro ao tentar abrir o arquivo {filepath}.")
        
    str_lines = " ".join(html_lines)
    dt_lines = str_lines.split('<br><dt>')

    text_sentences = []
    sentence_tokens = []
    count_sentences = 0
    count_tokens = 0

    for l in dt_lines:
        soup_line = BeautifulSoup(l, 'html.parser')
        linha = soup_line.text

        if "[" in linha:
            sentence_tokens.append(TokenVISL(count_tokens, *process_line(linha)))
            count_tokens += 1

        if MARK_END_SENTENCE in linha:
            if any(x in linha for x in PUNCT_CONTIN):
                continue

            if len(sentence_tokens) > 0:                
                idx_sentence = count_sentences                
                text_sentences.append(SentenceVISL(count_sentences,
                                                   sentence_tokens,
                                                   orig_sentences[idx_sentence]))
                count_sentences += 1
                count_tokens = 1
                sentence_tokens = []

    return DocVISL(text_sentences)

def has_mark_end(linha, _MARKS_END_SENTENCE):
    t0 = linha.split(' ')[0] 
    return (t0 in _MARKS_END_SENTENCE)
        

def parse_text_toclass(palavras_text, original_text):
    '''
    Parse line by line a file with PALAVRAS
    tags, stored with tags in text format
    '''   
    
    _MARK_END_SENTENCE = "$."
    _MARKS_END_SENTENCE = ["$.", "$?"]
    _MARK_WRONG_DQ = "$\""
    orig_sentences = []    
    orig_sentences = su.split_by_sentence(original_text)    
    dt_lines = []
    dt_lines = palavras_text.split('\n')

    text_sentences = []
    sentence_tokens = []
    idx_sentence = 0
    count_tokens = 0
    find_mark_end = False
    is_end_of_sentence = False

    for linha in dt_lines:
        if find_mark_end: 
            if len(linha) == 0: # linha com apenas um \n
                is_end_of_sentence = True
            elif has_mark_end(linha, [_MARK_WRONG_DQ]): # $. seguido de $"
                continue
            else:
                find_mark_end = False
        elif has_mark_end(linha, _MARKS_END_SENTENCE):
            find_mark_end = True
        
        #if _MARK_END_SENTENCE in linha:
        #    if any(x in linha for x in PUNCT_CONTIN):
        #        continue
        if is_end_of_sentence:
            if len(sentence_tokens) > 0:
                #idx_sentence = count_sentences
                text_sentences.append(SentenceVISL(idx_sentence,
                                                   sentence_tokens,
                                                   orig_sentences[idx_sentence]))
                idx_sentence += 1
                count_tokens = 1
                sentence_tokens = []
            
            is_end_of_sentence = False
        elif "[" in linha:
            sentence_tokens.append(TokenVISL(count_tokens, *process_line(linha)))
            count_tokens += 1

    # Algumas vezes o último token, não é seguido de um \n
    # ou é seguido por um $"
    if len(sentence_tokens) > 0:                
        text_sentences.append(SentenceVISL(idx_sentence,
                                            sentence_tokens,
                                            orig_sentences[idx_sentence]))

    return DocVISL(text_sentences)


def parse_file(filepath):
    '''
    Parse line by line a file with PALAVRAS
    tags, stored with html tags
    '''
    html_lines = []
    try:
        with open(filepath, 'r') as f_html:
            html_lines = f_html.readlines()
    except IOError:
        print(f"Erro ao tentar abrir o arquivo {filepath}.")
        
    str_lines = " ".join(html_lines)
    dt_lines = str_lines.split('<br><dt>')

    text_sentences = []
    sentence = []
    count_sentences = 1
    count_tokens = 1

    for l in dt_lines:
        soup_line = BeautifulSoup(l, 'html.parser')    
        linha = soup_line.text        
        token_1 = token_2 = token_3 = ""

        if "[" in linha:            
            sentence.append((count_tokens, *process_line(linha)))
            count_tokens += 1

        if MARK_END_SENTENCE in linha:
            if len(sentence) > 0:            
                text_sentences.append(tuple([count_sentences, sentence]))        
                count_sentences += 1
                count_tokens = 1
                sentence = []
    
    return text_sentences


def parse_html(text, tag_split='<br><dt>'):
    '''
    text it's a html text with tags and some marks, 
    result of PALAVRAS parsing process
    '''
    
    dt_lines = text.split(tag_split)

    text_sentences = []
    sentence = []
    count_sentences = 1
    count_tokens = 1

    for l in dt_lines:
        soup_line = BeautifulSoup(l, 'html.parser')    
        linha = soup_line.text        
        token_1 = token_2 = token_3 = ""

        if "[" in linha:            
            sentence.append((count_tokens, *process_line(linha)))
            count_tokens += 1

        if MARK_END_SENTENCE in linha:
            if len(sentence) > 0:            
                text_sentences.append(tuple([count_sentences, sentence]))        
                count_sentences += 1
                count_tokens = 1
                sentence = []
    
    return text_sentences


def parse_text(text):
    '''
    text it's a text with tags and some marks, 
    result of PALAVRAS parsing process
    '''
    _MARK_END_SENTENCE = "$."

    dt_lines = text.split("\n")

    text_sentences = []
    sentence = []
    count_sentences = 1
    count_tokens = 1

    for linha in dt_lines:        
        token_1 = token_2 = token_3 = ""

        if "[" in linha:            
            sentence.append((count_tokens, *process_line(linha)))
            count_tokens += 1

        if _MARK_END_SENTENCE in linha:
            if len(sentence) > 0:            
                text_sentences.append(tuple([count_sentences, sentence]))        
                count_sentences += 1
                count_tokens = 1
                sentence = []
    
    return text_sentences


def parse_PALAVRAS(text, output=None):
    '''
    Execute a request to VISL site, for parsing some piece of text
    '''
    parsed_text = None
    resp = None
    headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                "Accept-Encoding": "gzip, deflate", 
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
                "Dnt": "1", 
                "Host": "httpbin.org", 
                "Upgrade-Insecure-Requests": "1", 
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
              }
    url_endpoint = 'https://visl.sdu.dk/cgi-bin/visl.pt.cgi'        
    
    print(f"Processing text...")        

    dic_params = {'text': text,
                     'parser':'roles',
                     'visual':'cg-dep',
                     'heads':'',
                     'symbol':'unfiltered',
                     'multisearch':'',
                     'searchtype':'',
                     'inputlang':'pt'}

    print(f"Request to parsing text")        

    try:
        resp = requests.get(url_endpoint, headers=headers, params=dic_params)
        resp.raise_for_status()
        
        if resp.status_code == 200:
            print("Success on request!")
            parsed_text = resp.text            
            if output:
                print("Writing file... ")
                try:                
                    with open(f"{output}", "w") as f_redacao:
                        f_redacao.write(resp.text)
                except IOError:
                    print("I/O Error when writing file.")        
                    
            return parsed_text        
        else:
            print("Error on request. No data parsed.")
            
    except requests.exceptions.HTTPError as errh:
        print ("Http Error: ",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Connection Error: ",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout: ",errt)        
    
    return parsed_text
    

def test_parse_PALAVRAS():
    text_to_parse="O ser humano constrói seu caráter em sociedade. Primeiro no lar, na família e depois na Igreja ou qualquer outra instituição."
    r_parsed = parse_PALAVRAS(text_to_parse)
    s_parsed = BeautifulSoup(r_parsed)

    print(parse_text(s_parsed.text))

def show_annotated_example():
    text_annotated = """o [o] <*> <artd> DET M S @>N
    ser humano [ser=humano] <H> N M S @SUBJ>
    constrói [construir] <fmc> <vt> V PR 3S IND VFIN @FMV
    seu [seu] <poss 3S> <si> DET M S @>N
    caráter [caráter] <f-psych> N M S @<ACC
    em [em] PRP @<ADVL
    sociedade [sociedade] <HH> N F S @P<
    .
    primeiro [primeiro] <*> ADV @ADVL
    em [em] <sam-> PRP @ADVL
    o [o] <-sam> <artd> DET M S @>N
    lar [lar] <Lh> N M S @P<
    ,
    em [em] <sam-> PRP @ADVL
    a [o] <-sam> <artd> DET F S @>N
    família [família] <HH> N F S @P<
    e [e] KC @CO
    depois [depois] <atemp> ADV @ADVL
    em [em] <sam-> PRP @ADVL
    a [o] <-sam> <artd> DET F S @>N
    igreja [igreja] <prop> <*> <inst> N F S @P<
    ou [ou] KC @CO
    qualquer [qualquer] <quant> DET F S @>N
    outra [outro] <diff> <KOMP> DET F S @>N
    instituição [instituição] <inst> <act> N F S @NPHR
    ."""

    print("Annotated text example")
    print(text_annotated)
    print("\n")

    dt_lines = text_annotated.split("\n")
    text_sentences = []
    sentence = []
    count_sentences = 1
    count_tokens = 1

    print("dt_lines", len(dt_lines))
    for linha in dt_lines:        
        token_1 = token_2 = token_3 = ""

        if "[" in linha:            
            sentence.append((count_tokens, *process_line(linha)))
            count_tokens += 1

        if len(linha) == 1 and "." in linha:
            if len(sentence) > 0:            
                text_sentences.append(tuple([count_sentences, sentence]))        
                count_sentences += 1
                count_tokens = 1
                sentence = []

    print(text_sentences)