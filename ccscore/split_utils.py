# This code was adapted from Pedro 

import re, string, collections
import pandas as pd
from itertools import tee
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters, PunktLanguageVars


class PunctVars(PunktLanguageVars):
    sent_end_chars = ('.', '?', '!', ';')


punkt_param = PunktParameters()
punkt_param.abbrev_types = set([])
regex = re.compile('[%s]' % re.escape(string.punctuation))
substituicoes = {"Dr(a)": "Dr_a_", "Sr(a)": "Sr_a_", "Exmo(a)": "Exmo_a_"}
substituicoes_rev = {value: key for (key, value) in substituicoes.items()}


def sentence_tokenize(sentence_tokenizer, texto):
    '''
    Custom sentence tokenizer

    :param sentence_tokenizer: Tokenizer to use
    :param texto: text to be tokenized

    :return List of sentences tokenizeds
    '''

    l_sent_tokenizeds = sentence_tokenizer.tokenize(
                            multi_replace(texto, 
                                          substituicoes, 
                                          ignore_case=True)
                        )

    # regex used to detected sentence breaks with double (") 
    # without pair    
    double_quotes_only = r'^[^\"]*(\"[^\"]*\"[^\"]*)*(\")[^\"]*$'
    
    new_l_sent = []
    # if has just one sentence, not even look it 
    if len(l_sent_tokenizeds) == 1: 
        
        new_l_sent = l_sent_tokenizeds
    else:
        # if have two or more, try to reconect
        # in a way that double aspersand will be together
        a,b = tee(l_sent_tokenizeds)
        next(b)
        pares = list(zip(a,b))
        ignore_s1 = False
        s1 = s2 = None
        for s1,s2 in pares:        
            if re.match(double_quotes_only, s1) and \
            re.match(double_quotes_only, s2):
                new_l_sent.append(s1+s2)
                ignore_s1 = True
            elif ignore_s1:
                ignore_s1 = False
                continue
            else:
                new_l_sent.append(s1)
        
        if len(new_l_sent) < len(l_sent_tokenizeds):
            new_l_sent.append(s2)

    return [multi_replace(sentence, substituicoes_rev, ignore_case=True) for sentence in new_l_sent]


def multi_replace(string, replacements, ignore_case=False):
    """
    Given a string and a dict, replaces occurrences of the dict keys found in the
    string, with their corresponding values. The replacements will occur in "one pass",
    i.e. there should be no clashes.
    :param str string: string to perform replacements on
    :param dict replacements: replacement dictionary {str_to_find: str_to_replace_with}
    :param bool ignore_case: whether to ignore case when looking for matches

    :return Match list from compiled regex
    """
    if ignore_case:
        replacements = dict( ( pair[0].lower(), 
                               pair[1] ) 
                               for pair in sorted(replacements.items()))

    rep_sorted = sorted( replacements, 
                         key=lambda s: (len(s), s), 
                         reverse=True )

    rep_escaped = [re.escape(replacement) for replacement in rep_sorted]
    pattern = re.compile( "|".join(rep_escaped), re.I if ignore_case else 0 )

    return pattern.sub( lambda match: replacements[match.group(0).lower() 
                                                   if ignore_case else match.group(0)], 
                        string)


def split_by_break(texto):
    '''
    Tokenize text by break lines

    :param str texto: Text to be splitted

    '''
    texto = re.sub(r'[“”]', '"', texto)
    return [sentenca.strip() for sentenca in texto.splitlines()]


def startswith(quote_char, trecho, texto):
    '''
    Check if text starts with some quote and with a piece
    of text

    :param str quote_char: Quote to search
    :param trecho: Start text to search
    :param str texto: Text to search from

    :return bool If text starts with quote_char+text string
    '''
    return texto.startswith(quote_char + trecho)


def sanitize_split(texto, quote_chars=None, trechos=None):
    '''
    Sanitize the split removing useless punctuation

    :param str texto: Texto to sanitize
    :param list quote_char: Quote to remove
    :param list trechos: List of punctuations to remove

    :return str Sanitized text

    '''
    if quote_chars is None:
        quote_chars = ['"', '\'']
    if trechos is None:
        trechos = [' (...),', ' (...);', ' (...)', '(...)', '[...]',
                   ' ...', '...', '()', '),', ');', ')', ' ,', ' ;',
                   ' -', '•', ',', ';']
    texto = texto.strip()
    for quote_char in quote_chars:
        for trecho in trechos:
            if texto.count(quote_char) == 1:
                if startswith(quote_char, trecho, texto):
                    texto = texto.replace(quote_char + trecho, '')
            elif texto.count(quote_char) == 2:
                if texto.startswith(quote_char):
                    if texto.endswith(quote_char):
                        texto = texto[1:-1]
                        assert texto.count(quote_char) == 0
                        texto = texto.replace(trecho, '')
                    elif texto.endswith(quote_char + '.'):
                        texto = texto[1:-2]
                        assert texto.count(quote_char) == 0
                        texto = texto.replace(trecho, '')
        if texto.startswith(quote_char):
            patterns = ['\d+\.*', '^(\-*\d\s*\.*)*\-*\)*']
            for pattern in patterns:
                if re.fullmatch(pattern, texto[1:]):
                    texto = re.sub(pattern, '', texto)[1:]
    return texto.strip()


def split_by_sentence(texto, usar_ponto_virgula=False):
    '''
    Split a text by sentence

    :param str texto: Text to split
    :param bool usar_ponto_virgula: Use dot and comma punctuation to split

    :return list List of all sentences 
    '''
    if usar_ponto_virgula:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param, lang_vars=PunctVars())
    else:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param)
    if type(texto) == str:
        texto = re.sub(r'[“”]', '"', texto)
        return [sanitize_split(paragrafo) for paragrafo in sentence_tokenize(sentence_tokenizer, texto)]
    elif isinstance(texto, collections.Iterable):
        retorno = []
        for subtexto in texto:
            subtexto = re.sub(r'[“”]', '"', subtexto)
            retorno.extend(split_by_sentence(subtexto, usar_ponto_virgula))
        return retorno


def split(texto, usar_ponto_virgula=False):
    segmentos_por_quebra = split_by_break(texto)
    return split_by_sentence(segmentos_por_quebra, usar_ponto_virgula)
