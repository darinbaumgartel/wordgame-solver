import streamlit as st
import pickle
from streamlit import caching
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(layout="wide")

# Main navigation choices
main_nav = st.sidebar.selectbox(
    'Navigate',
    ("Try the algorithm", "Help picking a word")
)

# The ranked set of words
# This was derived from multiple corpuses scanning for 5-letter words
# Words are ordered by prevalence
ALL_WORDS_RANKED = []
with open ('words.pkl', 'rb') as fp:
    ALL_WORDS_RANKED = pickle.load(fp)


class Wordgame:    
    def __init__(self, 
                 target_word = None, 
                 hard_restrictions = None,
                 soft_restrictions = None, 
                 dne_restrictions = None,
                 viable_words = None
                ):
        self.target_word = target_word
        self.hard_restrictions = hard_restrictions or [None for ii in range(5)]
        self.soft_restrictions = soft_restrictions or []
        self.dne_restrictions = dne_restrictions or []
        if viable_words is None:
            self.viable_words = [x for x in ALL_WORDS_RANKED]
        else: 
            self.viable_words = viable_words
        self.update_viable_words_with_hard_restrictions()
        self.update_viable_words_with_soft_restrictions()
        self.update_viable_words_with_dne_restrictions()

        self.next_best_guess = None
    

    def update_viable_words_with_hard_restrictions(self):
        for ii in range(len(self.hard_restrictions)): 
            if self.hard_restrictions[ii] is not None: 
                self.viable_words = [x for x in self.viable_words if x[ii] == self.hard_restrictions[ii]]
            
    def update_viable_words_with_soft_restrictions(self):
        for character in self.soft_restrictions: 
            self.viable_words = [x for x in self.viable_words if character in x]
    
    def update_viable_words_with_dne_restrictions(self):
        for character in self.dne_restrictions: 
            self.viable_words = [x for x in self.viable_words if character not in x]

    def remove_viable_word(self, target_word):
        self.viable_words = [x for x in self.viable_words if x != target_word]            
    
    def set_hard_restrictions(self, hard_restrictions): 
        self.hard_restrictions = hard_restrictions
        self.update_viable_words_with_hard_restrictions()
   
    def set_soft_restrictions(self, soft_restrictions): 
        self.soft_restrictions = soft_restrictions
        self.update_viable_words_with_soft_restrictions()
        
    def set_dne_restrictions(self, dne_restrictions): 
        self.dne_restrictions = dne_restrictions
        self.update_viable_words_with_dne_restrictions()
        
    
    def report(self): 
        st.text ('spool' in self.viable_words) 
        st.text(f"Hard restrictions:{(self.hard_restrictions)}")
        st.text ('spool' in self.viable_words) 
        st.text(f"Soft restrictions:{(self.soft_restrictions)}")
        st.text ('spool' in self.viable_words) 
        st.text(f"DNE  restrictions:{(self.dne_restrictions)}")
        st.text ('spool' in self.viable_words) 
        st.text(f"Number of words:{len(self.viable_words)}")
        st.text ('spool' in self.viable_words) 
        st.text(f"Word examples:{self.viable_words[:50]}")
        st.text ('spool' in self.viable_words) 

        print('\n')

        
            
    def is_proper(word): 
        # Helper function to find words with upper case (proper words) for filtering
        for letter in word: 
            if letter.isupper():
                return True
        return False        
    
    def get_viable_count(self): 
        return len(self.viable_words)
    
    def is_done(self): 
        return len(self.viable_words) == 1

    def solution(self): 
        if self.is_done(): 
            return self.viable_words[0]
        else: 
            return None
            
    def guess_word(self, guess_word, target_word): 
        for ii in range(len(guess_word)): 
            if guess_word[ii] == target_word[ii]: 
                self.hard_restrictions[ii] = guess_word[ii]
            elif guess_word[ii] in target_word: 
                if guess_word[ii] not in self.soft_restrictions: 
                    self.soft_restrictions.append(guess_word[ii])
            else: 
                if guess_word[ii] not in self.dne_restrictions: 
                    self.dne_restrictions.append(guess_word[ii])
        self.update_viable_words_with_soft_restrictions()
        self.update_viable_words_with_dne_restrictions()        
        self.update_viable_words_with_hard_restrictions()  
        if not self.is_done():
            self.remove_viable_word(guess_word)      
            
    def get_next_best_guess(self): 
        current_words = [x for x in self.viable_words]
        if len(current_words) > 100: 
            current_words = current_words[:100]
        word_stats = {x:[] for x in current_words}
        for possible_target_word in current_words: 
            for guess_word in current_words: 
                test_wordgame = Wordgame(
                    hard_restrictions = [x for x in self.hard_restrictions], 
                    soft_restrictions = [y for y in self.soft_restrictions], 
                    dne_restrictions = [w for w in self.dne_restrictions],
                    viable_words = [z for z in current_words]                
                )
                    
                test_wordgame.guess_word(guess_word, possible_target_word)
                word_stats[guess_word].append(test_wordgame.get_viable_count())
                del test_wordgame
        
        word_scores = {word: round(sum(word_stats[word])/len(word_stats[word]),3) for word in word_stats} 
        word_scores_ranked = sorted(word_scores.items(), key=lambda x:x[1])
        self.next_best_guess = word_scores_ranked[0][0]



st.title(main_nav)

if main_nav == 'Try the algorithm':

	with st.form("new_dashboard_form"):
	    target_word = st.text_input("Try a 5-character word here", max_chars=5, value="smart" )
	    submitted = st.form_submit_button("Run auto-solver")
	if submitted: 

	    target_word = target_word.lower()
	    if len(target_word) != 5: 
	        st.warning("Word must be 5 characters")
	    elif not target_word.isalpha():
	        st.warning("Word must be just letters, no special characters")            
	    elif target_word not in ALL_WORDS_RANKED: 
	        st.warning(f"Word '{target_word}' does not exist.")
	    else:
	        w = Wordgame(hard_restrictions = [], soft_restrictions = [])
	        for ii in range(10): 
	            w.get_next_best_guess()
	            st.text(f"Attempt number #{ii+1}. {w.get_viable_count()} possibilites remain. Guessing '{w.next_best_guess}'")
	            w.guess_word(w.next_best_guess, target_word)
	            if w.solution() == w.next_best_guess: 
	                st.text (f"Found solution: {w.solution()}")
	                break         

	        del w 


elif main_nav == 'Help picking a word': 
	letters = 'abcdefghijklmnopqrstuvwxyz'
	letters = [x for x in letters]
	lunk = ['Unknown'] + letters 
	dne = options = st.text_input('Letters which have been ruled out (e.g. xyz):')
	dne = [x for x in dne]
	soft = options = st.text_input('Letters which are in the word, but you do not know the position of (e.g. abc):')
	soft = [x for x in soft]
	# hard = options = st.text_input('All letter position which are known (e.g. P*W**')
	c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
	with c1:
	    c1 = st.selectbox('First Letter', ['Unknown'] + letters)
	with c2:
	    c2 = st.selectbox('Second Letter', ['Unknown'] + letters)
	with c3:
	    c3 = st.selectbox('Third Letter', ['Unknown'] + letters)
	with c4:
	    c4 = st.selectbox('Fourth Letter', ['Unknown'] + letters)
	with c5:
	    c5 = st.selectbox('Fifth Letter', ['Unknown'] + letters)	    	    

	hard = []
	for x in [c1, c2, c3, c4, c5]: 
		if x != 'Unknown': 
			hard.append(x)
		else: 
			hard.append(None)

	st.write(f"\n\n")		
	st.write(f"Hard restrictions: {hard}")			
	st.write(f"Soft restrictions: {soft}")			
	st.write(f"Does-not-exist restrictions: {dne}")		
	st.write(f"\n\n")		

	try_wordgame = Wordgame(hard_restrictions = hard, soft_restrictions = soft, dne_restrictions = dne )
	try_wordgame.get_next_best_guess()
	st.write(f"This is the next best guess: \"{try_wordgame.next_best_guess}\"")
