### Hash table


TOO_FULL = 0.5
GROWTH_RATIO = 2


class HashTable:

    def __init__(self, cells, defval):
        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted
        '''

        self.size = cells
        self.num = 0
        self.defval = defval
        self.table = [[None, self.defval].copy() for i in range(self.size)]

    def __get_hash(self, key):
        '''
        Convert a string into a hash value
        '''

        h = 0
        k = 37

        for char in str(key):
            h = h * k + ord(char)

        return h % self.size

    def lookup(self, key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.
        '''

        h = self.__get_hash(key)
        val = self.defval
        stop = False
        found = False
        pos = h

        while (self.table[pos][0] is not None) and (not found) and (not stop):

            if self.table[pos][0] == key:
                found = True
                val = self.table[pos][1]

            else:
                pos = (pos + 1) % self.size

            if pos == h:
                stop = True

        return val

    def update(self, key, val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val".
        '''

        h = self.__get_hash(key)

        if self.table[h][0] is None:
            self.table[h][0] = key
            self.table[h][1] = val
            self.num += 1

        else:

            if self.table[h][0] == key:
                self.table[h][1] = val

            else:
                h = (h + 1) % self.size

                while (self.table[h][0] is not None) and \
                        (self.table[h][0] != key):
                    h = (h + 1) % self.size

                if self.table[h][0] is None:
                    self.table[h][0] = key
                    self.table[h][1] = val
                    self.num += 1

                else:
                    self.table[h][1] = val

        if self.num / self.size > TOO_FULL:
            self.__rehash()

    def __rehash(self):
        '''
        Expand the size of the hash table and migrate all the data into the
        proper location in the newly-expanded hash table once the fraction of
        occupied cells grows beyond the TOO_FULL after an update.∂
        '''
        keys = [pair[0] for pair in self.table if pair[0] is not None]
        vals = [pair[1] for pair in self.table if pair[1] != self.defval]

        self.num = 0
        self.size *= GROWTH_RATIO
        self.table = [[None, self.defval].copy() for i in range(self.size)]

        for k, v in zip(keys, vals):
            self.update(k, v)




import sys
import math
import hash_table

HASH_CELLS = 57


### Markov

class Markov:

    def __init__(self, k, s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''

        self._k = k
        self._s = s
        self.k_table, self.k1_table = self.learn()

    def get_k_k1(self, s):
        '''
        Given a string, return two lists of strings, one is the list of all 
        combination of consecutive k characters, while the other is the list 
        of all combination of consecutive k+1 characters
        '''

        s_ = s + s[:self._k]
        k_str = []
        k1_str = []
        for i in range(self._k, len(s_)):
            i_0 = s_[i - self._k:i]
            i_1 = s_[i]
            k_str.append(i_0)
            k1_str.append(i_0 + i_1)

        return k_str, k1_str

    def learn(self):
        '''
        Generate two hash tables for the k characters and k+1
        characters, where the key is the string and the 
        value is the frequencies
        '''

        k_hash = hash_table.HashTable(HASH_CELLS, None)
        k1_hash = hash_table.HashTable(HASH_CELLS, None)
        k_str, k1_str = self.get_k_k1(self._s)

        for i in range(len(k_str)):

            k1_value = k1_hash.lookup(k1_str[i])
            k_value = k_hash.lookup(k_str[i])

            if not k1_value:
                k1_hash.update(k1_str[i], 1)
            else:
                k1_hash.update(k1_str[i], k1_value + 1)

            if not k_value:
                k_hash.update(k_str[i], 1)
            else:
                k_hash.update(k_str[i], k_value + 1)

        return k_hash, k1_hash

    def log_probability(self, s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''

        prob = 0
        S = len(set(self._s))
        k_str, k1_str = self.get_k_k1(s)

        for i in range(len(k_str)):

            cnt = self.k1_table.lookup(k1_str[i])
            tot = self.k_table.lookup(k_str[i])
            if not cnt:
                cnt = 0
            if not tot:
                tot = 0
            prob += math.log((cnt + 1) / (tot + S))

        return prob


def identify_speaker(speaker_a, speaker_b, unknown_speech, k):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the
    speakers uttering that text under a "k" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''

    model_a = Markov(k, speaker_a)
    model_b = Markov(k, speaker_b)

    likelihood_a = model_a.log_probability(
        unknown_speech) / len(unknown_speech)
    likelihood_b = model_b.log_probability(
        unknown_speech) / len(unknown_speech)

    if likelihood_a > likelihood_b:
        conclusion = "A"
    else:
        conclusion = "B"

    return likelihood_a, likelihood_b, conclusion


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''

    (likelihood1, likelihood2, conclusion) = res_tuple

    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


def go():
    '''
    Interprets command line arguments and runs the Markov analysis.
    Useful for hand testing.
    '''
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)

    with open(sys.argv[1], "r") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "r") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "r") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)

if __name__ == "__main__":
    go()
