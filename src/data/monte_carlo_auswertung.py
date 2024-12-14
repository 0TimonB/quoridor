import pandas as pd
if __name__ == '__main__':
    data = pd.read_csv('monte_carlo_data.csv')
    print(data.head())
    time_depth = data.copy()[['monte_iter', 'time']].groupby(['monte_iter']).mean()
    print(time_depth.head(20))

    time_per_round_a_depth = data.copy()[['monte_iter', 'time_per_round_a']].groupby(
        ['monte_iter']).mean()
    print(time_per_round_a_depth.head(20))

    time_per_round_b_depth = data.copy()[['monte_iter', 'time_per_round_b']].groupby(
        ['monte_iter']).mean()
    print(time_per_round_b_depth.head(20))

    who_won_depth = data.copy()[['player_a','monte_iter', 'won']].groupby(['monte_iter']).value_counts()
    print(who_won_depth.head(20))