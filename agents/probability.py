import math

class Probability:

    @staticmethod
    def nCr(n, r):
        if r > -1 and r < n+1:
            return math.factorial(n)/(math.factorial(n-r) * math.factorial(r))
        else:
            return 0

    @staticmethod
    def model_probabilities(cards):
            combos = []
            for i in range(12):
                    common_suit = i//3
                    eight_suit = i%3 if i%3 < i//3 else (i%3)+1
                    suits = [0, 1, 2, 3]
                    suits.remove(common_suit)
                    suits.remove(eight_suit)
                    p = Probability.nCr(12, cards[common_suit]) * Probability.nCr(8, cards[eight_suit]) * Probability.nCr(10, cards[suits[0]]) * Probability.nCr(10, cards[suits[1]])
                    combos.append(p)
            likelihoods = [ combos[i] / sum(combos) for i in range(len(combos)) ]
            return likelihoods

    def expected_value(likelihoods, hand, card_index):
        
        common_suit = 0

        if card_index % 2 == 0:
            common_suit = card_index + 1
        else:
            common_suit = card_index - 1

        val = 0        
        start_index = common_suit * 3
        eight_index = start_index if common_suit < 2 else start_index+2
            

        for i in range(start_index, start_index + 3):
            
            if i == eight_index:
                if hand[card_index] > 4:
                    val += likelihoods[i] * 10
                else:
                    val += likelihoods[i] * (10 + 120/(5 - hand[card_index]) )

            else: 
                if hand[card_index] > 5:
                    val += likelihoods[i] * 10
                else:
                    val += likelihoods[i] * (10 + 100/(6 - hand[card_index]) )

        return val 
