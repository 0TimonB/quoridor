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

            #Wenn der aktive Spieler über den Anderen springt
            if current_player.blocks == 0 or self.board.player_a.node == self.board.player_b.node:
                blocking_invalid = True

                possible_moves = list(
                    nx.neighbors(self.board.graph, f'{current_player.node['row']},{current_player.node['col']}'))
                if (current_player.node['row'] == 0):
                    possible_moves.remove('Verbindung_zu_Reihe_0')
                elif (current_player.node['row'] == 8):
                    possible_moves.remove('Verbindung_zu_Reihe_8')
                next_node = {}
                while next_node == {}:
                    next_node = possible_moves[randint(0, len(possible_moves) - 1)]

                next_node_parts = next_node.split(',')
                if int(next_node_parts[0]) < current_player.node['row']:
                    action = 'move up'
                elif int(next_node_parts[0]) > current_player.node['row']:
                    action = 'move down'
                elif int(next_node_parts[1]) < current_player.node['col']:
                    action = 'move left'
                elif int(next_node_parts[1]) > current_player.node['col']:
                    action = 'move right'

            #Wenn der aktive Spieler nicht über den Anderen springt (Regelfall)
            else:
                blocking_invalid = False
                block_or_move = randint(1, 2)
                if block_or_move == 1:

                    possible_moves = list(
                        nx.neighbors(self.board.graph, f'{current_player.node['row']},{current_player.node['col']}'))
                    if(current_player.node['row'] == 0):
                        possible_moves.remove('Verbindung_zu_Reihe_0')
                    elif(current_player.node['row'] == 8):
                        possible_moves.remove('Verbindung_zu_Reihe_8')
                    next_node = {}
                    while next_node == {}:
                        next_node = possible_moves[randint(0, len(possible_moves) - 1)]

                    next_node_parts = next_node.split(',')
                    if int(next_node_parts[0]) < current_player.node['row']:
                        action = 'move up'
                    elif int(next_node_parts[0]) > current_player.node['row']:
                        action = 'move down'
                    elif int(next_node_parts[1]) < current_player.node['col']:
                        action = 'move left'
                    elif int(next_node_parts[1]) > current_player.node['col']:
                        action = 'move right'
                else:
                    if current_player == self.board.player_b:
                        blocking_nodes = list(nx.neighbors(self.board.graph, f'{self.board.player_a.node['row']},{self.board.player_a.node['col']}'))

                    else:
                        blocking_nodes = list(nx.neighbors(self.board.graph, f'{self.board.player_b.node['row']},{self.board.player_b.node['col']}'))

                    if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
                    if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

                    neighbour_nodes = []
                    for neighbour in blocking_nodes:
                        for neighbour_node in nx.neighbors(self.board.graph,
                                                           f'{neighbour.split(',')[0]},{neighbour.split(',')[1]}'):
                            neighbour_nodes.append(neighbour_node)
                    for neighbour in neighbour_nodes:
                        if not neighbour in blocking_nodes:
                            blocking_nodes.append(neighbour)

                    if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
                    if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')


                    random_node = blocking_nodes.pop(randint(0, len(blocking_nodes) - 1)).split(',')
                    while random_node == {}:
                        random_node = possible_nodes_for_blocking.pop(randint(0,len(possible_nodes_for_blocking) - 1))

                    random_orientation = 'horizontal' if randint(0, 1) == 0 else 'vertical'
                    action = f'block {random_node[0]} {random_node[1]} {random_orientation}'

            action_parts = action.split()

            move_ok = True
            #Prüfen des move Befehls
            if action_parts[0] == 'move' and len(action_parts) == 2:
                direction = action_parts[1]
                if not current_player.move(direction):
                    move_ok = False

            #Prüfen des block Befehls
            elif action_parts[0] == 'block' and len(action_parts) == 4:
                if blocking_invalid:
                    continue  # Gehe zurück zur Eingabeaufforderung
                row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
                if not current_player.place_blocking_element(row, col, orientation):
                    move_ok = False

            else:
                move_ok = False
                print(
                    "Ungültige Aktion. Bitte verwenden Sie 'move [direction]' oder 'block [row] [col] [orientation]'.")


            if move_ok:
                first_move = action if first_move == '' else first_move

            #Wechsel des Spielers oder nochmal, falls Spielzug ungültig
            if move_ok:
                current_player = self.board.player_b if current_player == self.board.player_a else self.board.player_a

            #Falls ein Spieler gerade über den anderen springt
            if blocking_invalid:
                #Falls der Sprung geklappt hat (aktualisierung der Symbole zur richtigen Darstellung)
                if not self.board.player_a.node == self.board.player_b.node:
                    self.board.player_b.node['symbol'] = 'B'
                    self.board.player_a.node['symbol'] = 'A'

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