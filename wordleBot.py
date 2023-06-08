## Wordle Bot 1.0
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

# Add letters that aren't in the word to the forbidden letter set
def add_forbidden_letters(guess, pattern):
    for i, letter in enumerate(guess):
        if pattern[i] < 1:
            forbidden.add(letter)
    return forbidden

# Calculate the current score of a guess. This is only used when the answer word is known
def calculate_score(guess, answer):
    pattern = [0] * 5
    used1 = [0] * 5
    used2 = [0] * 5

    for i, letter in enumerate(guess):
        forbidden.add(letter)
        if answer[i] == letter:
            pattern[i] = 2
            used1[i], used2[i] = 1, 1
            if letter in forbidden:
                forbidden.remove(letter)
    for a, l1 in enumerate(answer):
        if used1[a] == 1:
            continue
        else:
            for b, l2 in enumerate(guess):
                if used2[b] == 1:
                    continue
                elif l1 == l2:
                    used1[a], used2[b] = 1, 1
                    pattern[b] = 1
                    if l2 in forbidden:
                        forbidden.remove(l2)
                    break
    return pattern

# Add patterns to a set of patterns to avoid. This is to avoid placing letters in spots where they were previously yellow
def avoided_patterns(pattern, guess, avoiding):
    avoid = ''
    for i, letter in enumerate(guess):
        if pattern[i] < 2:
            avoid += letter
        else:
            avoid += '@'
    avoiding.add(avoid)

# Keep track of letters that are in the correct spot
def make_combos(pattern, guess):
    locks = ["@", "@", "@", "@", "@"]
    for i, correct in enumerate(pattern):
        if correct > 0:
            locks[i] = guess[i]
    return locks

# Make a set of all possible combos of the known letters
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

# Solve the wordle with a known answer
def solve(wordList, ans):
    guess = "salet"
    count = 0
    forbidden = set()
    
    while guess != ans:
        count = count + 1
        print("Num Guesses: " + str(count))
        print("GUESS:  " + guess + "   ANS:   " + ans)
        pattern = calculate_score(guess, ans)
        locks = make_combos(pattern, guess)
        p = compute_perms(locks, pattern)
        avoiding =  set()
        avoided_patterns(pattern, guess, avoiding)
        wordList = updateList1(wordList, avoiding)
        forbidden = add_forbidden_letters(guess, pattern)
        wordList = updateList3(wordList, forbidden, p)
        wordList, permToGuess = updateList2(wordList, p, guess)
        print(str(len(wordList)) + " possible words")
        if(len(wordList) == 0):
            print("No such word exists in the dictionary")
            return count
        guess = next_guess(wordList, permToGuess)
        if gameType != 't':
            print()
            print("Press Enter to Continue")
            x = input()
    count = count + 1

    print()
    print("Solution:  " + guess)
    print()
    print("SOLUTION TOOK " + str(count) + " guesses.")
    print()
    return count
    
# Calculate the average turns the bot takes to reach the answer
def compute_avg_guessesiciency(wordList):
    total = 0
    num = len(wordList)
    newList = wordList
    for ans in wordList:
        print(len(newList))
        count = solve(newList, ans)
        newList = wordList
        forbidden.clear()
        total += count
    return total / num

# Solve for an unknown word
def solve_unknown(wordList):
    count = 0
    guess = "salet"
    pattern = [0,0,0,0,0]
    avoiding = set()
    while pattern != [2,2,2,2,2]:
        count = count+1
        print("Num Guesses: " + str(count))
        print("GUESS:  " + guess + "   ANS:   ?")
        print()
        print("Enter the guess feedback (0 for grey, 1 for yellow, and 2 for green)")
        print("Example: 20011 would be the input for - green grey grey yellow yellow")
        inputx = input()
        pattern = [int(inputx[0]), int(inputx[1]), int(inputx[2]), int(inputx[3]), int(inputx[4])]
        locks = make_combos(pattern, guess)
        p = compute_perms(locks, pattern)
        avoided_patterns(pattern, guess, avoiding)
        wordList = updateList1(wordList, avoiding)
        forbidden = add_forbidden_letters(guess, pattern)
        wordList = updateList3(wordList, forbidden, p)
        wordList, permToGuess = updateList2(wordList, p, guess)
        print(str(len(wordList)) + " possible words")
        if(len(wordList) == 0):
            print("No such word exists in the dictionary")
            print()
            return count
        guess = next_guess(wordList, permToGuess)

    print("Solution took " + str(count) + " GUESSES.")
    return count

# Main function
def main():
    dictionary_file = sys.argv[1]
    print("Wordle Bot")
    print("Version 1.0")
    print("This version solves wordle in an average of 3.8 move if the word list is limited to just possible wordle answers (2309 possible words) \nand an average of 4.904 when the word list is expanded to all 5 letter words (12972 possible words)")
    print()
    print("To solve a wordle where the answer is unknown type 'u' \nTo give the bot a word to solve type 'k' \nTo test the efficiency of the bot type 't'\nType 'q' to quit")
    global forbidden
    global gameType
    gameType = input()
    while gameType != 'q':
        ans = ""
        forbidden = set()
        wordList = read_file(dictionary_file)
        if gameType =='k':
            os.system('clear')
            while len(ans) != 5:
                print("Enter a 5-letter word to solve:")
                ans = input()
            solve(wordList, ans)
        elif gameType == 't':
            print(compute_avg_guessesiciency(wordList))
        elif gameType == 'u':
            os.system('clear')
            solve_unknown(wordList)
        print("To solve a wordle where the answer is unknown type 'u' \nTo give the bot a word to solve type 'k' \nTo test the efficiency of the bot type 't'\nType 'q' to quit")
        gameType = input()
main()