"""
This program returns the greek texts scanning the text according to latin
accentuation rules.

A user is first prompted to supply the file path of the text they wish to scan.
Note that this text must be a relatively 'clean' text, as the opening function
(i.e., tokenize) will only remove numbers and all punctuation that is not a
period. The tokenizer will also force lower case on the text. The text will
then be tokenized and syllabified. Finally, the simplified tokenized text will be scanned according
to typical latin accentuation rules. The details of these rules are delineated in
the docstrings of the specific scansion functions. The final output is the
resulting scansion.

Known bugs:
1) Unknown
"""


#from cltk.utils.cltk_logger import logger

class ScanGreekWithLatinAccentuationRules:

    """Scans Greek texts, but does not macronize the text."""

    def __init__(self):
        """Setup class variables.
        :rtype: object
        """
        self.vowels = ['ε', 'ι', 'ο', 'α', 'η', 'ω', 'υ', 'ῖ', 'ᾶ']
        self.sing_cons = ['ς', 'ρ', 'τ', 'θ', 'π', 'σ', 'δ', 'φ', 'γ', 'ξ',
                          'κ', 'λ', 'χ', 'β', 'ν', 'μ']
        self.doub_cons = ['ξ', 'ζ', 'ψ']
        self.long_vowels = ['η', 'ω', 'ῖ', 'ᾶ', 'ῦ']
        self.diphthongs = ['αι', 'αῖ', 'ευ', 'εῦ', 'αυ', 'αῦ', 'οι', 'οῖ',
                           'ου', 'οῦ', 'ει', 'εῖ', 'υι', 'υῖ', 'ηῦ']
        self.stops = ['π', 'τ', 'κ', 'β', 'δ', 'γ']
        self.liquids = ['ρ', 'λ']
        self.punc = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                     '-', '_', '=', '+', '}', '{', '[', ']', '1', '2',
                     '3', '4', '5', '6', '7', '8', '9', '0', ',', '\'',
                     '᾽', '（', '）']
        self.punc_stops = ['·', ':', ';']

    def _clean_text(self, text):
        """Clean the text of extraneous punction.

        By default, ':', ';', and '.' are defined as stops.
        :param text: raw text
        :return: clean text
        :rtype : string
        """
        clean = []
        for char in text:
            if char in self.punc_stops:
                clean += '.'
            elif char not in self.punc:
                clean += char
            else:
                pass
        return (''.join(clean)).lower()

    def _clean_accents(self, text):
        """Remove most accent marks.

        Note that the circumflexes over alphas and iotas in the text since
        they determine vocalic quantity.
        :param text: raw text
        :return: clean text with minimum accent marks
        :rtype : string
        """
        accents = {
            'ὲέἐἑἒἓἕἔ': 'ε',
            'ὺύὑὐὒὓὔὕ': 'υ',
            'ὸόὀὁὂὃὄὅ': 'ο',
            'ὶίἰἱἲἳἵἴ': 'ι',
            'ὰάἁἀἂἃἅἄᾳᾂᾃ': 'α',
            'ὴήἠἡἢἣἥἤἧἦῆῄῂῇῃᾓᾒᾗᾖᾑᾐ': 'η',
            'ὼώὠὡὢὣὤὥὦὧῶῲῴῷῳᾧᾦᾢᾣᾡᾠ': 'ω',
            'ἶἷ': 'ῖ',
            'ἆἇᾷᾆᾇ': 'ᾶ',
            'ὖὗ': 'ῦ',
            }
        text = self._clean_text(text)
        for char in text:
            for key in accents.keys():
                if char in key:
                    text = text.replace(char, accents.get(key))
                else:
                    pass
        return text

    def _tokenize(self, text):
        """Tokenize the text into a list of words.

        :param text: raw text
        :return: tokenized text
        :rtype : list
        """
        word_list = []
        for word in self._clean_accents(text).split(' '):
            word_list.append(word)
        return word_list

    def _long_by_nature(self, syllable):
        """Check if syllable is long by nature.

        Long by nature includes:
        1) Syllable contains a diphthong
        2) Syllable contains a long vowel
        :param syllable: current syllable
        :return: True if long by nature
        :rtype : bool
        """
        # Find diphthongs
        vowel_group = []
        for char in syllable:
            if char in self.long_vowels:
                return True
            elif char not in self.sing_cons:
                vowel_group += char

        if ''.join(vowel_group) in self.diphthongs:
            return True

    def _long_by_position(self, syllable, word):
        """Check if syllable is long by position.

        Long by position includes:
        1) Next syllable begins with two consonants, unless those consonants
        are a stop + liquid combination
        2) Next syllable begins with a double consonant
        :param syllable: Current syllable
        :param word: Current word
        :return: True if syllable is long by position
        :rtype : bool
        """
        try:
            next_syll = word[word.index(syllable) + 1]
            # Long by position by case 1
            if (next_syll[0] in self.sing_cons and next_syll[1] in
                    self.sing_cons) and (next_syll[0] not in self.stops and
                                         next_syll[1] not in self.liquids):
                return True
            # Long by position by case 2
            elif syllable[-1] in self.vowels and next_syll[0] in self.doub_cons:
                return True
            else:
                pass
        except IndexError:
            logger.info("IndexError while checking if syllable '%s' is long. Continuing.", syllable)


    def _scansion(self, word_syll):
        """Replace long and short values for each input syllable.

        :param word_syll: A list of strings
        :return: '˘' and '¯' to represent short and long syllables,
        respectively
        :rtype : list
        """
        scanned_text = []
        for word in word_syll:
            ultima = len(word) -1
            penult = len(word) -2
            antepenult = len(word) -3
            scanned_word = []
            if len(word) == 1:
                scanned_word.append('O')
            elif len(word) == 2:
                for syll in word:
                    scanned_syllables = []
                    penult = '~'
                    scanned_syllables.append(penult)
                    ultima = '-'
                    scanned_syllables.append(ultima)
                scanned_word.append(scanned_syllables)
            elif len(word) >= 3:
                for syll in word:
                    scanned_syllables = []
                    if syll != ultima and penult and antepenult:
                        syll = '-'
                        scanned_syllables.append(syll)
                    elif self._long_by_position(penult, word) or self._long_by_nature(penult) == True:
                        antepenult = '-'
                        scanned_syllables.append(antepenult)
                        penult = '~'
                        scanned_syllables.append(penult)
                        ultima = '-'
                        scanned_syllables.append(ultima)
                    elif self._long_by_position(penult, word) or self._long_by_nature(penult) != True:
                        antepenult = '~'
                        scanned_syllables.append(antepenult)
                        penult = '-'
                        scanned_syllables.append(penult)
                        ultima = '-'
                        scanned_syllables.append(ultima)
                scanned_word.append(scanned_syllables)
            scanned_text.append(scanned_word)
        return scanned_text


    def _make_syllables(self, word_list):
        """Divide the word tokens into a list of syllables.

        Note that a syllable in this instance is defined as a vocalic group
        (i.e., vowel or a diphthong). This means that all syllables which are
        not the last syllable in the word will end with a vowel or diphthong.
        TODO: Determine whether a CLTK syllabifier could replace this
        :param word_list:
        :return: Syllabified words
        :rtype : list
        """
        text = self._tokenize(word_list)
        all_syllables = []
        for word in text:
            syll_start = 0  # Begins syllable iterator
            syll_per_word = []
            cur_letter_in = 0  # Begins general iterator
            while cur_letter_in < len(word):
                letter = word[cur_letter_in]
                if (cur_letter_in != len(word) - 1) and \
                    (word[cur_letter_in] + word[cur_letter_in + 1]) \
                    in self.diphthongs:
                    cur_letter_in += 1
                    # Syllable ends with a diphthong
                    syll_per_word.append(word[syll_start:cur_letter_in + 1])
                    syll_start = cur_letter_in + 1
                elif (letter in self.vowels) or (letter in self.long_vowels):
                    # Syllable ends with a vowel
                    syll_per_word.append(word[syll_start:cur_letter_in + 1])
                    syll_start = cur_letter_in + 1
                cur_letter_in += 1
            try:
                last_vowel = syll_per_word[-1][-1]  # Last vowel of a word
                # Modifies general iterator to accomodate consonants after
                # the last syllable in a word
                cur_letter_in = len(word) - 1
                # Contains all of the consonants after the last vowel in a word
                leftovers = ''
                while word[cur_letter_in] != last_vowel:
                    leftovers = word[cur_letter_in] + leftovers
                    cur_letter_in -= 1
                # Adds leftovers to last syllable in a word
                syll_per_word[-1] += leftovers
            except IndexError:
                logger.info("IndexError while making syllables of '%s'. Continuing.", word)
            all_syllables.append(syll_per_word)
        return all_syllables

    def scan_text(self, input_string):
        """The primary method for the class.

        :param input_string: A string of macronized text.
        :return: meter of latin accentuation rules applied to greek texts
        :rtype : list
        """
        word_syllables = self._make_syllables(input_string)
        meter = self._scansion(word_syllables)
        return meter

sample_text= "Προς τι; Στόχος αυτής της προσπάθειας είναιδημόσιο ή ιδιωτικό φορέα."
instance = ScanGreekWithLatinAccentuationRules()
instance.scan_text(sample_text)

