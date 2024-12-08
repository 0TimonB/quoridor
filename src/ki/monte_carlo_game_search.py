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

    def random_game(self, search_path):
        current_player = self.active_player
        first_move = ''
        while not self.board.player_a.won and not self.board.player_b.won:
            #mögliche nächste Züge
            possible_actions = []
                #mögliche Bewegungen erzeugen
            if first_move != '' or not search_path:
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
            if search_path and first_move == '':
                #falls search_path == true, wird beim ersten Zug der Bestmögliche zug 2 mal hinzugefügt
                if current_player.node['symbol'] == 'A':
                    path_search_graph = self.board.graph.copy()
                    path_search_graph.remove_node('Verbindung_zu_Reihe_0')
                    shortest_way = nx.shortest_path(path_search_graph, f"{current_player.node['row']},{current_player.node['col']}",'Verbindung_zu_Reihe_8')
                else:
                    path_search_graph = self.board.graph.copy()
                    path_search_graph.remove_node('Verbindung_zu_Reihe_8')
                    shortest_way = nx.shortest_path(path_search_graph, f"{current_player.node['row']},{current_player.node['col']}",'Verbindung_zu_Reihe_0')
                move_parts = shortest_way[1].split(',')
                best_move = ''
                if int(move_parts[0]) < current_player.node['row']:
                    best_move = 'move up'
                elif int(move_parts[0]) > current_player.node['row']:
                    best_move = 'move down'
                elif int(move_parts[1]) < current_player.node['col']:
                    best_move = 'move left'
                elif int(move_parts[1]) > current_player.node['col']:
                    best_move = 'move right'
                possible_actions.append(best_move)
                possible_actions.append(best_move)
                possible_actions.append(best_move)
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
                    if neighbour  not in blocking_nodes and neighbour not in self.board.nodes_used_for_blocking:
                        blocking_nodes.append(neighbour)
                if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
                if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

                #zulässige ermittelte Knoten zu möglichen Zügen hinzufügen
                for node in blocking_nodes:
                    split_node = node.split(',')
                    # if int(split_node[0]) != 8:
                    row = int(split_node[0])
                    col = int(split_node[1])

                    if not f'{row},{col}' in self.board.nodes_used_for_blocking:
                        self.pos_a = f'{row},{col}'
                        self.pos_b = f'{row + 1},{col}'
                        self.pos_c = f'{row},{col + 1}'
                        self.pos_d = f'{row + 1},{col + 1}'
                        if (self.pos_a, self.pos_b) in self.board.graph.edges and (
                        self.pos_c, self.pos_d) in self.board.graph.edges:
                            possible_actions.append(f"block {split_node[0]} {split_node[1]} horizontal")
                        if (self.pos_a, self.pos_c) in self.board.graph.edges and (
                        self.pos_b, self.pos_d) in self.board.graph.edges:
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


    def search_next_move(self, iterations, search_path):
        results = dict()
        current_player = self.active_player.node['symbol']
        for i in range(iterations):
            board = self.board.copy()
            monte_carlo = Monte_carlo_game_search(board,self.active_player)
            result, first_move = monte_carlo.random_game(search_path)
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