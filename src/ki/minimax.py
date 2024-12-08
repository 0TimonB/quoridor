import networkx as nx
from src.game.game import *
class MinimaxGameSearch:
    def __init__(self, board, active_player):
        self.board = board.copy()
        self.board.player_a.board = self.board
        self.board.player_b.board = self.board
        self.active_player = self.board.player_a if active_player.node['symbol'] == 'A' else self.board.player_b
        self.opponent = self.board.player_b if active_player == self.board.player_a else self.board.player_a

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_terminal_node():
            return self.evaluate_board(self.opponent if maximizing_player else self.active_player), None
        if maximizing_player:  # Maximizing player (current player)
            max_eval = -1000
            best_move = None
            for move in self.get_all_possible_moves(self.active_player):
                next_node = MinimaxGameSearch(self.board, self.active_player)
                next_node.perform_move(move)
                eval = next_node.minimax(depth - 1, alpha, beta, False)[0]
                #self.undo_move(move)

                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval, best_move
        else:  # Minimizing player (opponent)
            min_eval = 1000
            best_move = None
            for move in self.get_all_possible_moves(self.opponent):
                next_node = MinimaxGameSearch(self.board, self.active_player)
                next_node.perform_move(move)
                eval = next_node.minimax(depth - 1, alpha, beta, False)[0]
                #self.undo_move(move)



                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if alpha >= beta:
                    break
            return min_eval, best_move


    def is_terminal_node(self):
        return self.board.player_a.won or self.board.player_b.won

    def evaluate_board(self, current_player):

        # Kürzeste Distanz des aktiven Spielers zur Zielreihe
        player_a_graph = self.board.graph.copy()
        player_a_graph.remove_node('Verbindung_zu_Reihe_0')
        player_b_graph = self.board.graph.copy()
        player_b_graph.remove_node('Verbindung_zu_Reihe_8')

        player_a_dist = nx.shortest_path_length(
            player_a_graph, source=f'{self.board.player_a.node["row"]},{self.board.player_a.node["col"]}',
            target=f'Verbindung_zu_Reihe_8'  # Ziel für Spieler A
        )
        player_b_dist = nx.shortest_path_length(
            player_b_graph, source=f'{self.board.player_b.node["row"]},{self.board.player_b.node["col"]}',
            target=f'Verbindung_zu_Reihe_0'  # Ziel für Spieler B
        )

        # Bewertung aus Sicht des aktiven Spielers
        if current_player == self.board.player_a:
            # Spieler A versucht die eigene Distanz zu minimieren und die des Gegners zu maximieren
            score = player_b_dist
            #score += player_b_dist
            # Verbleibende Blockierungen als Bonus werten
            #score += self.board.player_a.blocks #- self.board.player_b.blocks
        else:
            # Spieler B versucht die eigene Distanz zu minimieren und die des Gegners zu maximieren
            score = player_a_dist
            #score += player_a_dist
            # Verbleibende Blockierungen als Bonus werten
            #score += self.board.player_b.blocks #- self.board.player_a.blocks

        return score

    def get_all_possible_moves(self, player):
        current_player = player

        # Überprüfe mögliche Bewegungen
        # mögliche nächste Züge
        possible_actions = []

        # mögliche Bewegungen erzeugen
        if current_player.node['symbol'] == 'A':
            path_search_graph = self.board.graph.copy()
            path_search_graph.remove_node('Verbindung_zu_Reihe_0')
            shortest_way = nx.shortest_path(path_search_graph,
                                            f"{current_player.node['row']},{current_player.node['col']}",
                                            'Verbindung_zu_Reihe_8')
        else:
            path_search_graph = self.board.graph.copy()
            path_search_graph.remove_node('Verbindung_zu_Reihe_8')
            shortest_way = nx.shortest_path(path_search_graph,
                                            f"{current_player.node['row']},{current_player.node['col']}",
                                            'Verbindung_zu_Reihe_0')
        move_parts = shortest_way[1].split(',')
        # mögliche Bewegungen zu möglichen Zügen hinzufügen
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

        # Füge mögliche Blockierungen hinzu
        #if current_player.blocks > 0 and self.board.player_a.node != self.board.player_b.node:
        #    possible_blocks = self.board.get_possible_blocks(self.board)
        #    for block in possible_blocks:
        #        split_block = block.split(',')
        #        possible_actions.append(f'block {split_block[0]} {split_block[1]} {split_block[2]}')

        # Welcher Spieler blockiert? + Nachbarknoten des Gegners hinzufügen
        if current_player == self.board.player_b:
            blocking_nodes = list(
                nx.neighbors(self.board.graph, f"{self.board.player_a.node['row']},{self.board.player_a.node['col']}"))

        else:
            blocking_nodes = list(
                nx.neighbors(self.board.graph, f"{self.board.player_b.node['row']},{self.board.player_b.node['col']}"))

        if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
        if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

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
        return possible_actions

    def is_valid_move(self, player, target):
        # Prüfen, ob der Knoten im richtigen Format 'row,col' vorliegt
        if isinstance(target, str) and ',' in target:
            row, col = map(int, target.split(','))
            return (0 <= row < self.board.size) and (0 <= col < self.board.size) and (self.board.graph.has_node(target))
        return False

    def perform_move(self, move):
        action_parts = move.split()
        action = action_parts[0]

        if action == "move":
            target = action_parts[1]
            self.active_player.move(target)
        elif action == "block":
            row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
            self.active_player.place_blocking_element(row, col, orientation)

    def undo_move(self, move):
        action_parts = move.split()
        action = action_parts[0]

        if action == "move":
            # Rückgängig machen des Moves (falls vorherige Position gespeichert wurde)
            target = action_parts[1]
            if target == 'up':
                target = 'down'
            elif target == 'down':
                target = 'up'
            elif target == 'left':
                target = 'right'
            elif target == 'right':
                target = 'left'
            self.active_player.move(target)
            pass
        elif action == "block":
            row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
            # Blockade rückgängig machen (Kante wieder hinzufügen etc.)
            if orientation == 'vertical':
                self.board.graph.add_edge(f"{row},{col}", f"{row + 1},{col}")
                self.board.graph.add_edge(f"{row},{col + 1}", f"{row + 1},{col + 1}")
            elif orientation == 'horizontal':
                self.board.graph.add_edge(f"{row},{col}", f"{row},{col + 1}")
                self.board.graph.add_edge(f"{row + 1},{col}", f"{row + 1},{col + 1}")
            pass

    def search_next_move(self, depth):
        _, best_move = self.minimax(depth, float('-inf'), float('inf'), True)
        return best_move


if __name__ == "__main__":
    board = Board(9)
    minimax_search = MinimaxGameSearch(board, board.player_a)
    print(minimax_search.search_next_move(3))  # Stellen Sie sicher, dass die Tiefe Ihren Anforderungen entspricht.