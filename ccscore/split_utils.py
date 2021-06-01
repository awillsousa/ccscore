import re, string, collections
import pandas as pd
from itertools import tee
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters, PunktLanguageVars


class JuridicoVars(PunktLanguageVars):
    sent_end_chars = ('.', '?', '!', ';')


punkt_param = PunktParameters()
#punkt_param.abbrev_types = set(pd.read_csv('lista_abreviacoes_lower.csv', header=None)[0].values)
punkt_param.abbrev_types = set([])
regex = re.compile('[%s]' % re.escape(string.punctuation))
substituicoes = {"Dr(a)": "Dr_a_", "Sr(a)": "Sr_a_", "Exmo(a)": "Exmo_a_"}
substituicoes_rev = {value: key for (key, value) in substituicoes.items()}


def sentence_tokenize(sentence_tokenizer, texto):
    l_sent_tokenizeds = sentence_tokenizer.tokenize(
                            multi_replace(texto, 
                                          substituicoes, 
                                          ignore_case=True)
                        )
    # regex utilizda para detectar quebras de sentenças contendo,
    # aspas duplas (") órfãs 
    double_quotes_only = r'^[^\"]*(\"[^\"]*\"[^\"]*)*(\")[^\"]*$'
    
    new_l_sent = []
    # se tiver apenas uma sentença, nem olha dá um desprezo
    if len(l_sent_tokenizeds) == 1: 
        
        new_l_sent = l_sent_tokenizeds
    else:
        # se tiver mais de uma, aí tenta reconectar as sentenças
        # de maneira a manter as aspas duplas na mesma sentença    
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
    :rtype: str the replaced string
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
    texto = re.sub(r'[“”]', '"', texto)
    return [sentenca.strip() for sentenca in texto.splitlines()]


def startswith(quote_char, trecho, texto):
    return texto.startswith(quote_char + trecho)


def sanitize_split(texto, quote_chars=None, trechos=None):
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
    if usar_ponto_virgula:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param, lang_vars=JuridicoVars())
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
