import re
import hashlib
from collections import Counter
import math

def tokenize(text):
    #returns a list of words
    return re.findall(r'\w', text)

def simhash(text):
    tokens = tokenize(text)
    v = [0] * 64

    #loop each word in the text
    for token in tokens:
        #converts the hexadecimal hash to integers
        hash = int(hashlib.md5(token.encode()).hexdigest(), 16)

        for i in range(64):
            #value of the ith bit
            bitmask = 2 ** i
            #if the i-th bit of h should hold a value
            if (hash & bitmask) != 0:
                #1 means bit is 1
                v[i] += 1
            else:
                #-1 means bit is 0
                v[i] -= 1
    #final 64-bit fingerprint
    fingerprint = 0
    for i in range(64):
        #if the bit is 1
        if v[i] > 0:
            #set the i-th bit of the fingerprint
            fingerprint = fingerprint | 2 ** i
        #v[i] < 0 means bit stays as 0
    return fingerprint
    
def hamming_distance(a,b):
    #XOR operation (counts total number of differing bits)
    return bin(a ^ b).count("1")

def get_first_element(x):
    return x[0]

def get_candidate_sets(left_lines, right_lines, k=15):
    #get simhash for all left lines
    left_hashes = []
    for l in left_lines:
        left_hash = simhash(l)
        left_hashes.append(left_hash)
    #get simhash for all right lines
    right_hashes = []
    for r in right_lines:
        right_hash = simhash(l)
        right_hashes.append(right_hash)

    #dict to store candidate sets
    candidates = {}

    #loop through each left lines hash
    for i, lh in enumerate(left_hashes):
        distances = []
        #compare to every right line's hash
        for j, rh in enumerate(right_hashes):
            #compute hamming distance of left hash with right hash
            dist = hamming_distance(lh, rh)
            #store distance and index of right hash
            distances.append((dist,j))
        #sort distances (smaller distance = more similar)
        distances.sort(key=get_first_element)
        candidates[i] = []
        #top 15 most similar right hashes are kept as candidates
        for dist, idx in distances[:k]:
            candidates[i].append(idx)
    return candidates
    
def levenshtein(a,b):
    #table of size len(a)+1 x len(b)+1
    table = [[0] * (len(b) + 1) for zero in range(len(a) + 1)]

    #initialize the first row and column
    for i in range(len(a) + 1):
        table[i][0] = i #removing costs
    for j in range(len(b) + 1):
        table[0][j] = j #inserting costs
    
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            if a[i-1] == b[j-1]:
                cost = 0
            else:#cost of substituting
                cost = 1
            table[i][j] = min(table[i-1][j] +1,       #remove last character from a
                              table[i][j-1] +1,       #add a character to a to match b
                              table[i-1][j-1] + cost) #replace the last character
    max_len = max(len(a), len(b))
    return 1 - table[-1][-1] / max_len

def cosine_similarity(a,b):
    #count num of words for lines a and b
    words_a = Counter(tokenize(a)) 
    words_b = Counter(tokenize(b))

    all_words = set(words_a.keys()) | set(words_b.keys())

    #product
    product = sum(words_a[w] * words_b[w] for w in all_words)

    #magnitudes
    mag_a = math.sqrt(sum(v * v for v in words_a.values()))
    mag_b = math.sqrt(sum(v * v for v in words_b.values()))

    if mag_b == 0 or mag_b == 0:
        return 0
    #cosine similarity
    return product / (mag_a * mag_b)

def combined_similarity(a,b):
    #similarity score
    return 0.6 * levenshtein(a,b) + 0.4 * cosine_similarity(a,b)

def best_matches(left_lines, right_lines, candidate_sets, threshold=0.5):
    final_matches = {}

    for left_idx, candidates in candidate_sets.items():
        best_score = -1
        best_match = None
        #check all candidates for left line
        for right_idx in candidates:
            score = combined_similarity(left_lines[left_idx], right_lines[right_idx])
            #keep track of highest score
            if score > best_score:
                best_score = score
                best_match = right_idx
        #score must be above threshold (0.5)
        if best_score >= threshold:
            final_matches[left_idx] = (best_match, best_score)
        else:
            final_matches[left_idx] = None
    
    return final_matches

#sample
left = ["linereader r = new linereader(fr);",
        "//change for reading"]
right = ["bufferedreader r = new bufferedreader(fr);",
         "Extra text case",
         "//change the reader"]
candidates = get_candidate_sets(left, right)
matches = best_matches(left, right, candidates)
for left_idx, match_info in matches.items():
    best_match_idx, score = match_info
    print(left_idx, "was matched with", best_match_idx)