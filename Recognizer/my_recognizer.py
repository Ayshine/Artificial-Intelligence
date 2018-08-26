import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
   
    for testing_word, (X, lengths) in test_set.get_all_Xlengths().items():

      best_score = float("-inf")
      best_guess = ""
      probability_dict = {}

      for trained_word, model in models.items():
        try:
          log_prob = model.score(X, lengths)
          probability_dict[trained_word] = log_prob

        except:
          probability_dict[trained_word] = float("-inf")

        if log_prob > best_score:
            best_score = log_prob
            best_guess = trained_word

      probabilities.append(probability_dict)
      guesses.append(best_guess)

    return probabilities, guesses

