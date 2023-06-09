## Wordle Bot v1.1
## Sean O'Sullivan
## 06-02-2023
from itertools import permutations
import os
import sys

# Read in words from dictionary file and return them as a list
def read_file(file):
    wordList = []
    words = open(file)
    for word in words:
        wordList.append(word[:5])
    return wordList

# Add forbidden letters to set
def add_forbidden_letters(guess, pattern, forbidden):
    for i, letter in enumerate(guess):
        if pattern[i] < 1:
            forbidden.add(letter)
    return forbidden

# Calculate the score of the computed guess
def calc_score(guess, answer):
    score = [0] * 5
    used_guess = [False] * 5
    used_answer = [False] * 5
    for i, g in enumerate(guess):
        forbidden.add(g)
        if answer[i] == g:
            score[i] = 2
            used_answer[i], used_guess[i] = True, True
        if g in forbidden:
                forbidden.remove(g)
    for i, a in enumerate(answer):
        if used_answer[i] == True:
            continue
        else:
            for j, g in enumerate(guess):
                if used_guess[j]:
                    continue
                elif a == g:
                    score[j] = 1
                    used_answer[i], used_guess[j] = True, True
                    if g in forbidden:
                        forbidden.remove(g)
                    break
    return score

# Create patterns that the bot should avoid guessing and add them to the set of avoided patterns
def avoided_patterns(pattern, guess, avoiding):
    avoid = ''
    for i, letter in enumerate(guess):
        if pattern[i] < 2:
            avoid += letter
        else:
            avoid += '@'
    avoiding.add(avoid)

# Create a list of letters that are known to be in the word and return them
def make_combos(pattern, guess):
    locks = ["@", "@", "@", "@", "@"]
    for i, correct in enumerate(pattern):
        if correct > 0:
            locks[i] = guess[i]
    return locks

# Compute all possible permutations the known letters of the word
def compute_perms(locks, pattern):
    perms2 = set()
    perms = [''.join(p) for p in permutations(locks)]
    for perm in perms:
        add = True
        for i, c in enumerate(locks):
            if c == '@':
                continue
            elif c != perm[i] and pattern[i] == 2:
                add = False
                break
            elif c == perm[i] and pattern[i] ==1:
                add = False
                break
        if add:
            perms2.add((perm,0))
    return [list(p) for p in perms2]

# Combine the permutaions of the previous and filler guess to create more specific permutations
def combine_perms(perms, fillerPerms, pattern):
    newPerms = []
    for perm in perms:
        for fillerPerm in fillerPerms:
            add = True
            newPerm = ''
            for i in range(5):
                if perm[0][i] != '@' and fillerPerm[0][i] != '@' and perm[0][i] != fillerPerm[0][i]:
                    add = False
                    break
                elif perm[0][i] != '@':
                    newPerm += perm[0][i]
                elif fillerPerm[0][i] != '@':
                    newPerm += fillerPerm[0][i]
                else:
                    newPerm += '@'
            if add:
                newPerms.append([newPerm, 0])
    return newPerms

# Update the list by removing words that have letters in spots that were previously yellow
def updateList1(wordList, avoidlist):
    updatedlist = set()
    for word in wordList:
        add = True
        for avoid in avoidlist:
            for i in range(0,5):
                if avoid[i] == word[i]:
                    add = False
        if add:
            updatedlist.add(word)
    return updatedlist

# Update list by removing words that don't have any of the possible permutations of the known letters
def updateList2(wordList, perms, lastGuess):
    newList = set()
    for word in wordList:
        for perm in perms:
            add = True
            for a, k in enumerate(perm[0]):
                if k == '@':
                    continue
                elif k != word[a]:
                    add = False
                    break
            if add and word != lastGuess:
                newList.add(word)
                perm[1] += 1
                break
    min = 1
    for p in perms:
        curr = entropy(p, newList)
        if min > curr:
            min = curr
            bestPerm = p
    return newList, bestPerm

# Update list by removing words that contain letters than are known to not be in the word
def updateList3(wordList, fset, perm):
    newList = set()
    for word in wordList:
        newList.add(word)
        for letter in fset:
            if word.count(letter) - perm[0][0].count(letter) > 0:
                newList.remove(word)
                break
    return newList
        
# Calculate which permutation narrows the wordlist down closest to half the list
def entropy(perm, wordList):
    if len(wordList) == 0:
        return 0
    q = abs(0.5 - (perm[1]/len(wordList)-0.001))
    return q

# Return a word to guess that has the givern permutation
def next_guess(wordList, perm):
    print()
    for word in wordList:
        add = True
        for a, k in enumerate(perm[0]):
            if k != word[a] and k != '@':
                add = False
                break
        if add:
            return word

# Return a filler word that will help narrow down the list of words that all have the same known permutation
def filler_word(wordList, fullList, locks):
    charCount = [0] * 26
    for word in wordList:
        for i in range(len(word)):
            if locks.count(word[i]) == 0:
                charCount[ord(word[i]) - 97] += 1
    maxLetters = 0
    topWord = ""
    for word in fullList:
        curr = 0
        for i, char in enumerate(charCount):
            if char > 0 and word.count(chr(i + 97)) and locks.count(char) == 0:
                curr += 1
        if curr > maxLetters:
            topWord = word
            maxLetters = curr
    return topWord

# Calculate the average turns the bot takes to reach the answer
def compute_avg_guesses(wordList):
    total = 0
    num = len(wordList)
    newList = wordList
    for ans in wordList:
        print(len(newList))
        count = solve_known(newList, ans)
        newList = wordList
        forbidden.clear()
        total += count
    return total / num

# Solve the wordle with a known answer
def solve_known(wordList, answer):
    locks = ["@", "@", "@", "@", "@"]
    count = 0
    forbidden = set()
    guess = "salet"
    filler = False
    perms1 = ["@@@@@"]
    while guess != answer:
        count = count + 1
        print()
        print("Num Guesses: " + str(count))
        print("GUESS:  " + guess + "   ANS:   " + answer)
        print()
        pattern = calc_score(guess, answer)
        locks = make_combos(pattern, guess)
        print(pattern)
        if not filler:
            perms1 = compute_perms(locks, pattern)
            perm = perms1
        else:
            perms2 = compute_perms(locks, pattern)
            perm = combine_perms(perms1, perms2, pattern)
        avoiding =  set()
        avoided_patterns(pattern, guess, avoiding)
        wordList = updateList1(wordList, avoiding)
        forbidden = add_forbidden_letters(guess, pattern, forbidden)
        wordList = updateList3(wordList, forbidden, perm)
        wordList, permToGuess = updateList2(wordList, perm, guess)
        perms1 = perm
        print(str(len(wordList)) + " possible words")
        if(len(wordList) == 0):
            print("No such word exists in the dictionary")
            return count
        guess = next_guess(wordList, permToGuess)
        newGuess = filler_word(wordList, fullList, locks)
        filler = False
        if len(perm) < 2 and perm[0][1] > 2 or (len(perm) == 2 and (perm[1][1] < 2 and perm[0][1] > 2)) or (len(perm) == 2 and (perm[0][1] < 2 and perm[1][1] > 2)):
            guess = newGuess
            filler = True
        if gameType != 't':
            wait = input()
    count += 1
    print()
    print("Solution is: " + guess)
    print()
    print("Solution took " + str(count) + " guesses.")
    print()
    return count

# Solve for an unknown word
def solve_unknown(wordList):
    count = 0
    guess = "salet"
    pattern = [0,0,0,0,0]
    avoiding = set()
    forbidden = set()
    filler = False
    while pattern != [2,2,2,2,2]:
        inputx = ""
        count = count+1
        print("Num Guesses: " + str(count))
        print("GUESS:  " + guess + "   ANS:   ?")
        print()
        while(inputx.count('0') + inputx.count('1') + inputx.count('2') != 5 or len(inputx) != 5):
            print("Enter the guess feedback (0 for grey, 1 for yellow, and 2 for green)")
            print("Example: 20011 would be the input for - green grey grey yellow yellow")
            inputx = input()
        pattern = [int(inputx[0]), int(inputx[1]), int(inputx[2]), int(inputx[3]), int(inputx[4])]
        if pattern == [2,2,2,2,2]:
            break
        locks = make_combos(pattern, guess)
        if not filler:
            perms1 = compute_perms(locks, pattern)
            perm = perms1
        else:
            perms2 = compute_perms(locks, pattern)
            perm = combine_perms(perms1, perms2, pattern)
        avoiding =  set()
        avoided_patterns(pattern, guess, avoiding)
        wordList = updateList1(wordList, avoiding)
        forbidden = add_forbidden_letters(guess, pattern, forbidden)
        wordList = updateList3(wordList, forbidden, perm)
        wordList, permToGuess = updateList2(wordList, perm, guess)
        perms1 = perm
        print(str(len(wordList)) + " possible words")
        if(len(wordList) == 0):
            print("No such word exists in the dictionary")
            return count
        guess = next_guess(wordList, permToGuess)
        newGuess = filler_word(wordList, fullList, locks)
        filler = False
        if len(perm) < 2 and perm[0][1] > 2 or (len(perm) == 2 and (perm[1][1] < 2 and perm[0][1] > 2)) or (len(perm) == 2 and (perm[0][1] < 2 and perm[1][1] > 2)):
            guess = newGuess
            filler = True
    print()
    print("Solution is:  " + guess)
    print("Solution took " + str(count) + " guesses.")
    print()
    return count

# Main function
def main():
    global dictionary_file
    global answers_file
    dictionary_file = sys.argv[1]
    answers_file = sys.argv[2]
    
    print("Wordle Bot v1.1")
    print("This version solves wordle in an average of:")
    print("3.755 moves when the valid guess list is the full dictionary (12,972 words) and the valid solutions list is limited to valid wordle solutions (2,309 words).")
    print("3.749 moves when the valid guess list is limited to valid wordle solutions and the valid solutions list is also limited to valid wordle solutions.")
    print("4.567 moves when the valid guess list is the full dictionary list and the valid solutions list is also the full dictionary list.")
    print()
    print("To solve a wordle where the answer is unknown type 'u' \nTo give the bot a word to solve type 'k' \nTo test the efficiency of the bot type 't'\nType 'q' to quit")
    global forbidden
    global gameType
    gameType = input()
    while gameType != 'q':
        ans = ""
        forbidden = set()
        wordList = read_file(answers_file)
        global fullList
        fullList = read_file(dictionary_file)
        if gameType =='k':
            os.system('clear')
            while len(ans) != 5:
                print("Enter a 5-letter word to solve:")
                ans = input()
            solve_known(wordList, ans)
        elif gameType == 't':
            print(compute_avg_guesses(wordList))
        elif gameType == 'u':
            os.system('clear')
            solve_unknown(wordList)
        print("To solve a wordle where the answer is unknown type 'u' \nTo give the bot a word to solve type 'k' \nTo test the efficiency of the bot type 't'\nType 'q' to quit")
        gameType = input()
main()