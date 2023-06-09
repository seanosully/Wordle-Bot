# Wordle-Bot v1.1
 
 To run the program:
  python3 wordleBot.py <path to dictionary file (All-Words.txt or Possible-Answers.txt) > <path to valid solutions file (All-Words.txt or Possible-Answers.txt)>

Current stats:
 When using the All-Words dictionary file which contains 12,903 words the bot will average ~4.9 guesses to find the solution
 When using the Possible-Answers dictionary file which only contains valid Wordle answers it averages ~3.8 guesses to find the solution
 
 # Three Modes
 This bot can be used to play Wordle by inputting the result of each guess. 0 is used to signify a gray square, 1 yellow, and 2 green.
 For example:
 ⬜🟩⬜🟩🟨 --> 02021
 🟩🟩🟩🟩🟩 --> 22222
 
 There is also a mode where you can give the bot a word to solve
 The last mode is to run the bot against all the words in the dictionary file and have it output the average guesses needed.
 
 * Note: The bot is not optimal yet
