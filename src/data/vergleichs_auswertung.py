import pandas as pd
if __name__ == '__main__':
    data = pd.read_csv('data.csv')
    #print(data.head())
    first_player_ai_mean_time_game = data.copy()[['player_a', 'time']].groupby(['player_a']).mean()
    print(first_player_ai_mean_time_game.head(20))

    print()

    who_won_first_player_ai = data.copy()[['player_a', 'won']].groupby(['player_a']).value_counts()
    print(who_won_first_player_ai.head(20))
