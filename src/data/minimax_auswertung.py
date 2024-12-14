import pandas as pd
if __name__ == '__main__':
    data = pd.read_csv('data_minimax.csv')
    #print(data.head())
    time_depth = data.copy()[['minimax_depth', 'time']].groupby(['minimax_depth']).mean()
    time_depth['time'] = time_depth['time'].map('{:,.2f}'.format)
    print(time_depth.head(20))
    print()

    time_per_round_a_depth = data.copy()[['minimax_depth', 'time_per_round_a']].groupby(
        ['minimax_depth']).mean()
    time_per_round_a_depth['time_per_round_a'] = time_per_round_a_depth['time_per_round_a'].map('{:,.2f}'.format)
    print(time_per_round_a_depth.head(20))
    print()

    time_per_round_b_depth = data.copy()[['minimax_depth', 'time_per_round_b']].groupby(
        ['minimax_depth']).mean()
    time_per_round_b_depth['time_per_round_b'] = time_per_round_b_depth['time_per_round_b'].map('{:,.2f}'.format)
    print(time_per_round_b_depth.head(20))

    print()

    who_won_depth = data.copy()[['minimax_depth', 'won']].groupby(['minimax_depth']).value_counts()
    print(who_won_depth.head(20))