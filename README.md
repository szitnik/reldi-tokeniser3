# reldi-tokeniser

A tokeniser developed inside the [ReLDI project](https://reldi.spur.uzh.ch). Supports three languages -- Croatian, Serbian and Slovene, and two modes -- for standard and non-standard text.

## Usage

```
$ echo 'kaj sad s tim.daj se nasmij ^_^. | ./tokeniser.py hr -n
1.1.1.1-3	kaj
1.1.2.5-7	sad
1.1.3.9-9	s
1.1.4.11-13	tim
1.1.5.14-14	.

1.2.1.15-17	daj
1.2.2.19-20	se
1.2.3.22-27	nasmij
1.2.4.29-31	^_^
1.2.5.32-32	.


```

Language is a positional argument while tokenisation of non-standard text is an optional one.

## Programmatic usage

```
    tokenizer3 = ReldiTokeniser3("standard", "sl")

    print(tokenizer3.processText("Jaz sem šel v trgovino. Kupil sem banane in kruh.\n Nekaj me je presenetilo."))

  This will print output as follows:
    [[['1.1.1.1-3', 'Jaz'], ['1.1.2.5-7', 'sem'], ['1.1.3.9-11', 'šel'], ['1.1.4.13-13', 'v'],
    ['1.1.5.15-22', 'trgovino'], ['1.1.6.23-23', '.']], [['1.2.1.25-29', 'Kupil'], ['1.2.2.31-33', 'sem'], ['1.2.3.35-40', 'banane'],
    ['1.2.4.42-43', 'in'], ['1.2.5.45-48', 'kruh'], ['1.2.6.49-49', '.']], [['2.1.1.1-5', 'Nekaj'], ['2.1.2.7-8', 'me'],
    ['2.1.3.10-11', 'je'], ['2.1.4.13-23', 'presenetilo'], ['2.1.5.24-24', '.']]]
```
