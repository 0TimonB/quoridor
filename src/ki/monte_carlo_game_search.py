import networkx as nx
from src.game.game import *
from random import randint

class Monte_carlo_game_search:
    def __init__(self, board, active_player):
        self.board = board.copy()
        if active_player.node['symbol'] == 'A':
            self.active_player = self.board.player_a
            self.board.player_b.blocks = 0
        else:
            self.active_player = self.board.player_b
            self.board.player_a.blocks = 0

    def random_game(self):
        current_player = self.active_player
        first_move = ''
        possible_nodes_for_blocking = list(self.board.graph.nodes().values()).copy()
        while not self.board.player_a.won and not self.board.player_b.won:
            #mögliche nächste Züge
            possible_actions = []
            #mögliche Bewegungen erzeugen
            possible_moves = list(
                nx.neighbors(self.board.graph, f"{current_player.node['row']},{current_player.node['col']}"))
            if (current_player.node['row'] == 0):
                possible_moves.remove('Verbindung_zu_Reihe_0')
            elif (current_player.node['row'] == 8):
                possible_moves.remove('Verbindung_zu_Reihe_8')
            while {} in possible_moves:
                possible_moves.remove({})
            #mögliche Bewegungen zu möglichen Zügen hinzufügen
            for move in possible_moves:
                move_parts = move.split(',')
                if int(move_parts[0]) < current_player.node['row']:
                    possible_actions.append('move up')
                elif int(move_parts[0]) > current_player.node['row']:
                    possible_actions.append('move down')
                elif int(move_parts[1]) < current_player.node['col']:
                    possible_actions.append('move left')
                elif int(move_parts[1]) > current_player.node['col']:
                    possible_actions.append('move right')

            #blockieren
            if current_player.blocks > 0 and self.board.player_a.node != self.board.player_b.node:
                #Welcher Spieler blockiert? + Nachbarknoten des Gegners hinzufügen
                if current_player == self.board.player_b:
                    blocking_nodes = list(nx.neighbors(self.board.graph,f"{self.board.player_a.node['row']},{self.board.player_a.node['col']}"))

                else:
                    blocking_nodes = list(nx.neighbors(self.board.graph,f"{self.board.player_b.node['row']},{self.board.player_b.node['col']}"))

                if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
                if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

                #Nachbar-nachbar-Knoten hinzufügen
                neighbour_nodes = []
                for neighbour in blocking_nodes:
                    for neighbour_node in nx.neighbors(self.board.graph,f"{neighbour.split(',')[0]},{neighbour.split(',')[1]}"):
                        neighbour_nodes.append(neighbour_node)
                for neighbour in neighbour_nodes:
                    if not neighbour in blocking_nodes:
                        blocking_nodes.append(neighbour)
                if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
                if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

                #zulässige ermittelte Knoten zu möglichen Zügen hinzufügen
                for node in blocking_nodes:
                    if node not in self.board.nodes_used_for_blocking:
                        split_node = node.split(',')
                        if int(split_node[0]) != 8:
                            possible_actions.append(f"block {split_node[0]} {split_node[1]} horizontal")
                            possible_actions.append(f"block {split_node[0]} {split_node[1]} vertical")

            #zufälligen Zug aus den möglichkeiten ausführen
            action = possible_actions[randint(0, len(possible_actions) - 1)]
            action_parts = action.split()

            if action_parts[0] == 'move':
                current_player.move(action_parts[1])
            else:
                if not current_player.place_blocking_element(int(action_parts[1]), int(action_parts[2]), action_parts[3]):
                    continue

            #Wechsel des Spielers oder nochmal, falls Sprung
            if self.board.player_a.node is not self.board.player_b.node:
                current_player = self.board.player_b if current_player == self.board.player_a else self.board.player_a

            self.board.player_b.node['symbol'] = 'B'
            self.board.player_a.node['symbol'] = 'A'


            first_move = action if first_move == '' else first_move

        #Spiel beendet, Ausgabe des Gewinners
        if self.board.player_a.won:
            return 'A', first_move
        else:
            return 'B', first_move


    def search_next_move(self, iterations):
        results = dict()
        current_player = self.active_player.node['symbol']
        for i in range(iterations):
            board = self.board.copy()
            monte_carlo = Monte_carlo_game_search(board,self.active_player)
            result, first_move = monte_carlo.random_game()
            if first_move not in list(results.keys()):
                results[first_move] = [0, 0]
                results[first_move][0] = 1 if result == current_player else 0
                results[first_move][1] = results[first_move][1] + 1
            else:
                results[first_move][0] = results[first_move][0] + 1 if result == current_player else \
                results[first_move][0]
                results[first_move][1] = results[first_move][1] + 1
        final_results = dict()
        for key in results.keys():
            final_results[key] = results[key][0] / results[key][1]
        return(self.key_of_max(final_results))

    def key_of_max(self,d):
        return max(d, key=d.get)


if __name__ == "__main__":
    board = Board(9)
    monte_carlo = Monte_carlo_game_search(board,board.player_a)
    print(monte_carlo.search_next_move(1000))