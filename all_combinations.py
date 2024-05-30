import pandas as pd
import itertools
from ast import literal_eval

max_loop = 19545240
buffer = []
csv_idx = 0

collected = pd.Series({
    "stone":0,
    "animal":0,
    "plant":0,
    
    "clue":0,
    "night":0,
    
    "blue":0,
    "green":0,
    "red":0,
    "yellow":0,
    
    "score":0,
})

class Sanctuary():
    def __init__(self, color, night=False, clue=False, ressources=[], reward_type='fix', reward_value=0):
        self.color = color
        
        self.night=night
        self.clue=clue
        
        self.ressources=ressources
        self.reward_type=reward_type
        self.reward_value=reward_value
        
    def compute_reward(self, collected):
        if isinstance(self.reward_type, list):
            value = 0
            for type in self.reward_type:
                value += collected[type]*self.reward_value 
            return value
                
        elif self.reward_type == 'fix':
            return self.reward_value
        elif self.reward_type == 'multi':
            return collected[['blue', 'green', 'red', 'yellow']].min()*self.reward_value
        else:
            return collected[self.reward_type]*self.reward_value 
        
    def get_reward(self, collected):
        return self.compute_reward(collected)
    
    def get_ressources(self, collected):
        collected[self.color] += 1
        
        if self.night:
            collected["night"] += 1
            
        if self.clue:
            collected["clue"] += 1
            
        for ressource in self.ressources:
            collected[ressource] += 1
            
        collected['score'] += self.get_reward(collected)


class Card(Sanctuary):
    def __init__(self, color, number, night=False, clue=False, ressources=[], requirements=[], reward_type='fix', reward_value=0):
        super().__init__(color=color, night=night, clue=clue, ressources=ressources, reward_type=reward_type, reward_value=reward_value)
        
        self.number = number
        self.requirements = pd.Series(requirements).value_counts().to_dict()
        
    def get_reward(self, collected):
        if all([collected[type]>=number for type, number in self.requirements.items()]):
            return self.compute_reward(collected)
        else :
            return 0
        
def compute_score(sequence, card_df):
    collected = pd.Series({
    "stone":0,
    "animal":0,
    "plant":0,
    
    "clue":0,
    "night":0,
    
    "blue":0,
    "green":0,
    "red":0,
    "yellow":0,
    
    "score":0,
    })

    for i in sequence:
        card_df.loc[i]['instance'].get_ressources(collected)
        
    return collected['score']
        
card_df = pd.read_csv('all_cards.csv')
for col in ['ressources', 'requirements','reward_type']:
    card_df[col]=card_df[col].apply(lambda x : x if x[0]!='[' else literal_eval(x))
card_df = card_df.set_index('number', drop=False)
card_df['instance'] = card_df.apply(lambda x : Card(color=x['color'], number=x['number'], night=x['night'], clue=x['clue'], ressources=x['ressources'], 
                                  requirements=x['requirements'], reward_type=x['reward_type'],reward_value=x['reward_value']), axis=1)

for i, permutation in enumerate(itertools.permutations(range(1,69), r=8)):
    if i%max_loop != 0:
        buffer.append(permutation)
    else:
        sequence = pd.DataFrame(data={'sequence':buffer}, dtype='object')
        sequence['score'] = sequence['sequence'].apply(lambda x : compute_score(x, card_df))
        sequence = sequence[sequence['score']>50]
        sequence.to_csv(f'data\\all_combinations_{csv_idx}.csv', index=False)
        print(f"Save csv number {csv_idx}, best score {sequence['score'].max()}")
        
        buffer = []
        csv_idx += 1