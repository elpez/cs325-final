# CS325 Topic Proposal - Machine Translation
## Henry Mohr and Ian Fisher

We are proposing to build a rule-based machine translation algorithm from Spanish to English. We will use the TBL algorithm to tag the Spanish text, then shallow parsing to build syntax trees, and finally syntactic and lexical transfer to translate the trees to English. Our syntactic transfer algorithm will use simple transformation rules like Adj N → N Adj. We will need a tagged Spanish corpus with which to train our TBL tagger. The cess_esp is just such a corpus, available on nltk and tagged with the [EAGLES](http://www.ilc.cnr.it/EAGLES96/annotate/annotate.html) tagset. For lexical transfer, we will use a simple Spanish-English dictionary, such as the one [here](http://www.dicts.info/uddl.php).
