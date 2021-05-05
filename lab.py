# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, key_type):
        self.value = None
        self.key_type = key_type
        self.children = {}

    def _valid_key(self, key):
        if type(key) != self.key_type:
            raise TypeError(f'Given key\'s type does not match the key type of {self.key_type} for this Trie')

    def _find_trie(self, key):
        """
        Returns the trie at the inputed key. If the key does not exist in then
        it raises a KeyError, and raises a TypeError if the given key is of the 
        wrong type.
        """
        self._valid_key(key)
        cur_trie = self
        for k in key:
            if self.key_type == tuple:
                k = (k,)
            if k in cur_trie.children:
                cur_trie = cur_trie.children[k]
            else:
                raise KeyError(f'Given key, {key}, was not found in the Trie')
        return cur_trie

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        self._valid_key(key)
        cur_key = key[0]
        if self.key_type == tuple:
            cur_key = (key[0],)    
        if not cur_key in self.children:
            # create new Trie instance
            cur = Trie(self.key_type)
            self.children[cur_key] = cur
        else:
            # grab the existing Trie instance at this key
            cur = self.children[cur_key]
        if len(key) == 1:
            # if it is the last value in the key, then set the value of this Trie
            self.children[cur_key].value = value
        else:
            # recursively call, set item again with rest of key
            cur[key[1:]] = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> x = Trie(str)
        >>> t = Trie(str)
        >>> t['bat'] = True
        >>> t['bat']
        True
        """
        return self._find_trie(key).value

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bat'] = True
        >>> t['bar'] = False
        >>> del t['bat']
        """
        t = self._find_trie(key)
        if t.value == None:
            raise KeyError(f'Given key, {key}, was not found in the Trie')
        t.value = None

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        >>> t = Trie(str)
        >>> t['bat'] = True
        >>> t['bar'] = False
        >>> 'bat' in t
        True
        >>> 'bank' in t
        False
        >>> 'bar' in t
        True
        """
        try:
            t = self._find_trie(key)
            if t.value == None:
                return False
            return True
        except KeyError:
            return False
    
    def recursive_generator(self, key, trie):
        if trie.value != None:
            yield (key, trie.value)
        for k, t in trie.children.items():
            yield from self.recursive_generator(key+k, trie.children[k])

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        if self.key_type == tuple:
            yield from self.recursive_generator((), self)
        else:
            yield from self.recursive_generator('', self)


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    >>> t = make_word_trie("code code and more code")
    >>> t['and']
    1
    >>> t['code']
    3
    """
    word_trie = Trie(str)
    sentences = tokenize_sentences(text)
    for s in sentences:
        for w in s.split(" "):
            if w in word_trie:
                word_trie[w] += 1
            else:
                word_trie[w] = 1
    return word_trie

def get_sentence_tuple(sentence):
    """
    Takes in a sentence and returns a tuple of the words in that sentence
    """
    sent_tuple = ()
    for word in sentence.split(" "):
        sent_tuple += (word,)
    return sent_tuple

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    >>> t = make_phrase_trie("I like waffles. I like french toast.")
    >>> t[('i', 'like', 'waffles')]
    1
    >>> t[('i', 'like', 'french', 'toast')]
    1
    """
    phrase_trie = Trie(tuple)
    sentences = tokenize_sentences(text)
    for s in sentences:
        sent_tuple = get_sentence_tuple(s)
        if sent_tuple in phrase_trie:
            phrase_trie[sent_tuple] += 1
        else:
            phrase_trie[sent_tuple] = 1
    return phrase_trie

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    >>> t = make_word_trie("bat bat bark bar")
    >>> autocomplete(t, "ba", 1)
    ['bat']
    >>> t_test = autocomplete(t, "ba", 3)
    >>> 'bat' in t_test and 'bar' in t_test and 'bark' in t_test and len(t_test) == 3
    True
    >>> autocomplete(t, "be", 2)
    []
    >>> x = make_word_trie("lemonade lemon leprechaun")
    >>> x_test = autocomplete(x, "lem", 3)
    >>> 'lemon' in x_test and 'lemonade' in x_test and len(x_test) == 2
    True
    """
    try:
        t = trie._find_trie(prefix)
        # iterates over the words that have the prefix and saves them in a frequency map with the key being
        # the value of that word in the trie and the key's value is a set of the words that have the same count
        freq_map = {}
        max_freq = None
        for e in t:
            count = e[1]
            if count in freq_map:
                freq_map[count] |= { e[0] }
            else:
                freq_map[count] = { e[0] }
            if not max_freq or count > max_freq:
                max_freq = count
        # starting from the highest frequency count of a word seen in the trie with the prefix, it loops from
        # there down, adding words to the element list until it reaches the size of max_count or runs out of words
        # if max_count is not set
        element_list = []
        for i in range(max_freq, 0, -1):
            if i in freq_map:
                for w in freq_map[i]:
                    if max_count == None or len(element_list) < max_count:
                        element_list.append(prefix+w)
                    else:
                        break
        return element_list
    except KeyError:
        # if the prefix isn't in the trie, then find trie raises a keyerrro and it returns an empty array
        return []

def get_single_insertions(prefix):
    """
    Yields all possible single-character insertions (add any one character in the range "a" to "z" at any place in the word)
    """
    letters = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(prefix)+1):
        for l in letters:
            yield prefix[:i] + l + prefix[i:]

def get_single_deletions(prefix):
    """
    # Yields all possible single-character deletions (remove any one character from the word)
    """
    for i in range(len(prefix)):
        yield prefix[:i] + prefix[i+1:]

def get_single_replacement(prefix):
    """
    Yields all possible single-character replacements (replace any one character in the word with a character in the range a-z)
    """
    letters = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(prefix)):
        for l in letters:
            yield prefix[:i] + l + prefix[i+1:]

def get_two_char_transpose(prefix):
    """
    Yields all possible two-character transposes (switch the positions of any two adjacent characters in the word)
    """
    for i in range(len(prefix)-1):
        for j in range(i+1, len(prefix)):
            yield prefix[:i] + prefix[j] + prefix[i+1:j] + prefix[i] + prefix[j+1:]

def get_edits(prefix):
    """
    Yields all possible edits
    """
    yield from get_single_insertions(prefix)
    yield from get_single_deletions(prefix)
    yield from get_single_replacement(prefix)
    yield from get_two_char_transpose(prefix)

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    >>> t = make_word_trie("code code and more coding")
    >>> a = autocomplete(t, "co", 2)
    >>> "code" in a and "coding" in a and len(a) == 2
    True
    >>> a = autocomplete(t, "co", 1)
    >>> "code" in a and len(a) == 1
    True
    """
    element_list = autocomplete(trie, prefix, max_count)
    # if autocomplete didn't return enough elements or max_count is not set, then 
    # look for valid edits of the prefix
    if max_count == None or len(element_list) < max_count:
        # gets most-frequently-occuring valid edits of the prefix until the length of 
        # the element list hits max count or gets all if max count is not set
        freq_map = {}
        max_freq = None
        used_words = set(element_list)
        # loop over possible edits of the prefix
        for word in get_edits(prefix):
            # if they are valid, then add them to the freq map
            if not word in used_words and word in trie:
                count = trie[word]
                if count in freq_map:
                    freq_map[count] |= { word }
                else:
                    freq_map[count] = { word }
                if not max_freq or count > max_freq:
                    max_freq = count
        # loop over the values in the freq map starting from the highest count and going down
        for i in range(max_freq, 0, -1):
            if i in freq_map:
                for w in freq_map[i]:
                    # add elements to list until size of element list hits max_count or until
                    # it runs out of words if max_count is not set
                    if max_count == None or len(element_list) < max_count:
                        element_list.append(w)
                    else:
                        break
    return element_list
    
def search(trie, pattern, word):
    """
    Recursive search function for finding words that match the pattern
    Returns a set of words that match pattern
    """
    if not pattern:
        if word in trie:
            return {(word, trie[word])}
        return set()
    matches = set()
    if pattern[0] == "*":
        # remove any immediately following * to prevent it from adding in the same word multiple times
        while len(pattern) > 1 and pattern[1] == '*':
            pattern = pattern[1:]
        # no char works
        matches |= search(trie, pattern[1:], word)
        # and all next chars work
        for c in trie._find_trie(word).children:
            matches |= search(trie, pattern, word+c)
            if len(pattern) > 1 and c == pattern[1]:
                matches |= search(trie, pattern[1:], word+c)
    elif pattern[0] == "?":
        # must have a next char which can be anything
        for c in trie._find_trie(word).children:
            matches |= search(trie, pattern[1:], word+c)
    else:
        # p is a specific char
        try:
            if trie._find_trie(word+pattern[0]):
                matches |= search(trie, pattern[1:], word+pattern[0])
        except KeyError:
            pass
    return matches


def word_filter(trie, pattern, word=None, seen=None):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    >>> t = make_word_trie("bar bark bat bat")
    >>> f = word_filter(t, "*")
    >>> ('bat', 2) in f and ('bar', 1) in f and ('bark', 1) in f and len(f) == 3
    True
    >>> f = word_filter(t, "???")
    >>> ('bat', 2) in f and ('bar', 1) in f and len(f) == 2
    True
    >>> f = word_filter(t, "*r*")
    >>> ('bar', 1) in f and ('bark', 1) in f and len(f) == 2
    True
    """
    matches = search(trie, pattern, "")
    return list(matches)


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    doctest.testmod()

    # t = Trie(tuple)
    # t[2, ] = 'cat'
    # t[(1, 2, 3)] = 'kitten'
    # t[(1, 2, 0)] = 'tricycle'
    # t[(1, 2, 0, 1)] = 'rug'
    # print(t[(1, 2, 3)])
    # print(t[(1, 2, 0)])
    # print(t[(1, 2, 0, 1)])
    # t[1, 0, 0] = 'dog'
    # t[1, 0, 1] = 'ferret'
    # t[1, 0, 1, 80] = 'tomato'

    # trie = make_word_trie("cats cattle hat car act at chat crate act car act")
    # print(autocorrect(trie, 'cat', 4))
    # assert set(result) == {"act", "car", "cats", "cattle"}
    # t = make_word_trie("bar bark bat bat")
    # print(word_filter(t, "*r*"))
    
    # w = make_word_trie('bringing clinging')
    # print(word_filter(w, '*ing'))

    # with open("text_files/alices_adventures.txt", encoding="utf-8") as f:
    #     text = f.read()

    #     phrase_trie = make_phrase_trie(text)
    #     # six_most_common_sent = autocomplete(phrase_trie, (), 6)
    #     # print(six_most_common_sent)

    #     # word_trie = make_word_trie(text)
    #     # top_12_autocorrects = autocorrect(word_trie, "hear", 12)
    #     # print(top_12_autocorrects)

    #     total_sent = 0
    #     distinct_sent = 0
    #     for i in phrase_trie:
    #         total_sent += i[1]
    #         distinct_sent += 1
    #     print(total_sent, distinct_sent)

    # with open("text_files/metamorphisis.txt", encoding="utf-8") as f:
    #     text = f.read()

    #     word_trie = make_word_trie(text)
    #     six_most_common_words = autocorrect(word_trie, "gre", 6)
    #     print(six_most_common_words)

    #     all_words_with_pattern = word_filter(word_trie, "c*h")
    #     print(all_words_with_pattern)

    # with open("text_files/dracula.txt", encoding="utf-8") as f:
    #     text = f.read()

    #     word_trie = make_word_trie(text)
    #     total_words = 0
    #     distinct_words = 0
    #     for i in word_trie:
    #         total_words += i[1]
    #         distinct_words += 1
    #     print(total_words, distinct_words)

    # with open("text_files/tale_of_two_cities.txt", encoding="utf-8") as f:
    #     text = f.read()

    #     word_trie = make_word_trie(text)
    #     all_word_matching_pattern = word_filter(word_trie, "r?c*t")
    #     print(all_word_matching_pattern)
