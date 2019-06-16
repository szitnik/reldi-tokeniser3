#!/usr/bin/python
#-*-encoding:utf-8-*-


"""

    tokenizer3 = ReldiTokeniser3("standard", "sl")

    print(tokenizer3.processText("Jaz sem šel v trgovino. Kupil sem banane in kruh.\n Nekaj me je presenetilo."))

  This will print output as follows:
    [[['1.1.1.1-3', 'Jaz'], ['1.1.2.5-7', 'sem'], ['1.1.3.9-11', 'šel'], ['1.1.4.13-13', 'v'],
    ['1.1.5.15-22', 'trgovino'], ['1.1.6.23-23', '.']], [['1.2.1.25-29', 'Kupil'], ['1.2.2.31-33', 'sem'], ['1.2.3.35-40', 'banane'],
    ['1.2.4.42-43', 'in'], ['1.2.5.45-48', 'kruh'], ['1.2.6.49-49', '.']], [['2.1.1.1-5', 'Nekaj'], ['2.1.2.7-8', 'me'],
    ['2.1.3.10-11', 'je'], ['2.1.4.13-23', 'presenetilo'], ['2.1.5.24-24', '.']]]

"""

import re
import codecs
import sys

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 

import os

class ReldiTokeniser3:

    def __init__(self, mode, lang):
        self.reldir = os.path.dirname(os.path.abspath(__file__))
        self.abbrevs = {
          'hr': self.read_abbrevs('hr.abbrev'),
          'sr': self.read_abbrevs('hr.abbrev'),
          'sl': self.read_abbrevs('sl.abbrev')
        }

        self.num = r'(?:(?<!\d)[+-])?\d+(?:[.,:/]\d+)*(?:[.](?!\.)|-[^\W\d_]+)?'
        # emoswithspaces emoticon=r'[=:;8][\'-]*(?:\s?\)+|\s?\(+|\s?\]+|\s?\[+|\sd\b|\sp\b|d+\b|p+\b|s+\b|o+\b|/|\\|\$|\*+)|-\.-|\^_\^|\([\W]+\)|<3|</3|<\\3|\\o/'
        self.emoticon = r'[=:;8][\'-]*(?:\)+|\(+|\]+|\[+|d\b|p\b|d+\b|p+\b|s+\b|o+\b|/|\\|\$|\*+)|-\.-|\^_\^|\([^\w\s]+\)|<3|</3|<\\3|\\o/'
        self.word = r'(?:[*]{2,})?\w+(?:[@­\'-]\w+|[*]+\w+)*(?:[*]{2,})?'

        self.langs = {
          'hr': {
            'abbrev': r'|'.join(self.abbrevs['hr']['B'] + self.abbrevs['hr']['N'] + self.abbrevs['hr']['S']),
            'num': self.num,
            'url': r'https?://[-\w/%]+(?:[.#?=&@;][-\w/%]+)+|\b\w+\.(?:\w+\.)?(?:[a-z]{3,4})/?\b',
            'htmlesc': r'&#?[a-z0-9]+;',
            'tag': r'</?[a-z][\w:]*>|<[a-z][\w:]*/?>',
            'mail': r'[\w.-]+@\w+(?:[.-]\w+)+',
            'mention': r'@[a-z0-9_]+',
            'hashtag': r'#\w+(?:[.-]\w+)*',
            'emoticon': self.emoticon,
            'word': self.word,
            'arrow': r'<[-]+|[-]+>',
            'dot': r'[.!?/]{2,}',
            'space': r'\s+',
            'other': r'(.)\1*',
            'order': (
            'abbrev', 'num', 'url', 'htmlesc', 'tag', 'mail', 'mention', 'hashtag', 'emoticon', 'word', 'arrow', 'dot',
            'space', 'other')
          },

          'sr': {
            'abbrev': r'|'.join(self.abbrevs['sr']['B'] + self.abbrevs['sr']['N'] + self.abbrevs['sr']['S']),
            'num': self.num,
            'url': r'https?://[-\w/%]+(?:[.#?=&@;][-\w/%]+)+|\b\w+\.(?:\w+\.)?(?:[a-z]{3,4})/?\b',
            'htmlesc': r'&#?[a-z0-9]+;',
            'tag': r'</?[a-z][\w:]*>|<[a-z][\w:]*/?>',
            'mail': r'[\w.-]+@\w+(?:[.-]\w+)+',
            'mention': r'@[a-z0-9_]+',
            'hashtag': r'#\w+(?:[.-]\w+)*',
            'emoticon': self.emoticon,
            'word': self.word,
            'arrow': r'<[-]+|[-]+>',
            'dot': r'[.!?/]{2,}',
            'space': r'\s+',
            'other': r'(.)\1*',
            'order': (
            'abbrev', 'num', 'url', 'htmlesc', 'tag', 'mail', 'mention', 'hashtag', 'emoticon', 'word', 'arrow', 'dot',
            'space', 'other')
          },

          'sl': {
            'abbrev': r'|'.join(self.abbrevs['sl']['B'] + self.abbrevs['sl']['N'] + self.abbrevs['sl']['S']),
            'num': self.num,
            'url': r'https?://[-\w/%]+(?:[.#?=&@;][-\w/%]+)+|\b\w+\.(?:\w+\.)?(?:[a-z]{3,4})/?\b',
            'htmlesc': r'&#?[a-z0-9]+;',
            'tag': r'</?[a-z][\w:]*>|<[a-z][\w:]*/?>',
            'mail': r'[\w.-]+@\w+(?:[.-]\w+)+',
            'mention': r'@[a-z0-9_]+',
            'hashtag': r'#\w+(?:[.-]\w+)*',
            'emoticon': self.emoticon,
            'word': self.word,
            'arrow': r'<[-]+|[-]+>',
            'dot': r'[.!?/]{2,}',
            'space': r'\s+',
            'other': r'(.)\1*',
            'order': (
            'abbrev', 'num', 'url', 'htmlesc', 'tag', 'mail', 'mention', 'hashtag', 'emoticon', 'word', 'arrow', 'dot',
            'space', 'other')
          }
        }

        # transform abbreviation lists to sets for lookup during sentence splitting
        for lang in self.abbrevs:
          for type in self.abbrevs[lang]:
            self.abbrevs[lang][type] = set([e.replace('\\.', '.') for e in self.abbrevs[lang][type]])

        self.spaces_re = re.compile(r'\s+', re.UNICODE)
        self.mode = mode
        self.token_re = None
        self.lang = lang
        self.generate_tokenizer(self.lang)

    def processText(self, text):
        retVal = []
        for par_id, line in enumerate(text.splitlines()):
            processedLine = self.processLine(line)

            token_id = 0
            sent_id = 0
            for sent in processedLine:
                sent_id += 1
                token_id = 0
                sentenceTokens = []
                for token, start, end in sent:
                    if not token[0].isspace():
                        token_id += 1
                        globalTokenId = str(par_id+1) + '.' + str(sent_id) + '.' + str(token_id) + '.' + str(
                            start + 1) + '-' + str(end)
                        sentenceTokens.append([globalTokenId, token])
                retVal.append(sentenceTokens)
        return retVal


    def processLine(self, line):
        if self.mode == "standard":
            return self.sentence_split(self.tokenize(self.token_re, line), self.lang)
        elif self.mode == "nonstandard":
            return self.sentence_split_nonstd(self.tokenize(self.token_re, line), self.lang)
        else:
            raise ValueError('Mode not correctly set!')

    def read_abbrevs(self, file):
        abbrevs={'B':[],'N':[],'S':[]}
        for line in open(os.path.join(self.reldir,file)):
          if not line.startswith('#'):
            abbrev,type=line.strip().split('\t')[:2]
            abbrev,type=line.strip().split('\t')[:2]
            abbrevs[type].append(abbrev)
        return abbrevs

    def generate_tokenizer(self, lang):
        els=self.langs[lang]
        token_re=re.compile(r'|'.join([self.langs[lang][e] for e in self.langs[lang]['order']]),re.UNICODE|re.IGNORECASE)
        self.token_re = token_re

    def tokenize(self, tokenizer,paragraph):
        return [(e.group(0),e.start(0),e.end(0)) for e in tokenizer.finditer(paragraph.strip())]#spaces_re.sub(' ',paragraph.strip()))]

    def sentence_split_nonstd(self, tokens,lang):
        boundaries=[0]
        for index in range(len(tokens)-1):
          token=tokens[index][0]
          if token[0] in u'.!?…': #if sentence ending punctuation
            boundaries.append(index+1)
          elif token.endswith('.'): #if abbreviation
            if token.lower() not in self.abbrevs[lang]['N']: #if not in non-splitting abbreviations
              if token.lower() in self.abbrevs[lang]['S']: #if in splitting abbreviations
                boundaries.append(index+1)
              elif len(token)>2:
                if tokens[index+1][0][0].isupper(): #else if next is uppercase
                  boundaries.append(index+1)
                  continue
                if index+2<len(tokens): # else if next is space and nextnext is uppercase
                  if tokens[index+1][0][0].isspace() and tokens[index+2][0][0].isupper():
                  #tokens[index+1][0][0] not in u'.!?…':
                    boundaries.append(index+1)
        boundaries.append(len(tokens))
        sents=[]
        for index in range(len(boundaries)-1):
          sents.append(tokens[boundaries[index]:boundaries[index+1]])
        return sents

    def sentence_split(self, tokens,lang):
        boundaries=[0]
        for index in range(len(tokens)-1):
          token=tokens[index][0]
          if token[0] in u'.!?…' or (token.endswith('.') and token.lower() not in self.abbrevs[lang]['N'] and len(token)>2 and tokens[index+1][0][0] not in u'.!?…'):
            if tokens[index+1][0][0].isupper():
              boundaries.append(index+1)
              continue
            if index+2<len(tokens):
              if tokens[index+2][0][0].isupper():
                if tokens[index+1][0].isspace() or tokens[index+1][0][0] in u'-»"\'':
                  boundaries.append(index+1)
                  continue
            if index+3<len(tokens):
              if tokens[index+3][0][0].isupper():
                if tokens[index+1][0].isspace() and tokens[index+2][0][0] in u'-»"\'':
                  boundaries.append(index+1)
                  continue
            if index+4<len(tokens):
              if tokens[index+4][0][0].isupper():
                if tokens[index+1][0].isspace() and tokens[index+2][0][0] in u'-»"\'' and tokens[index+3][0][0] in u'-»"\'':
                  boundaries.append(index+1)
                  continue
        boundaries.append(len(tokens))
        sents=[]
        for index in range(len(boundaries)-1):
          sents.append(tokens[boundaries[index]:boundaries[index+1]])
        return sents



    def represent_tomaz(self, input,par_id):
        output=''
        token_id=0
        sent_id=0
        for sent in input:
          sent_id+=1
          token_id=0
          for token,start,end in sent:
            if not token[0].isspace():
              token_id+=1
              output+=str(par_id)+'.'+str(sent_id)+'.'+str(token_id)+'.'+str(start+1)+'-'+str(end)+'\t'+token+'\n'
          output+='\n'
        return output


if __name__=='__main__':
  import argparse
  parser=argparse.ArgumentParser(description='Tokeniser for (non-)standard Slovene, Croatian and Serbian')
  parser.add_argument('lang',help='language of the text',choices=['sl','hr','sr'])
  parser.add_argument('-n','--nonstandard',help='invokes the non-standard mode',action='store_true')
  args=parser.parse_args()
  lang=args.lang
  mode='standard'
  if args.nonstandard:
    mode='nonstandard'

  tokenizer3 = ReldiTokeniser3(mode, lang)

  par_id=0
  for line in sys.stdin:
    par_id+=1
    sys.stdout.write(tokenizer3.represent_tomaz(tokenizer3.processLine(line), par_id))
