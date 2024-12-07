import networkx as nx
from src.game.game import *


class MinimaxGameSearch:
    def __init__(self, board, active_player):
        self.board = board.copy()
        self.active_player = self.board.player_a if active_player.node['symbol'] == 'A' else self.board.player_b
        self.opponent = self.board.player_b if active_player == self.board.player_a else self.board.player_a

    def minimax(self, depth, alpha, beta, maximizing_player, lowest_move):
        if depth == 0 or self.is_terminal_node():
            return self.evaluate_board(), lowest_move

        if maximizing_player:  # Maximizing player (current player)
            max_eval = float('-inf')
            best_move = None
            for move in self.get_all_possible_moves(self.active_player):
                self.perform_move(move)
                eval = self.minimax(depth - 1, alpha, beta, False, move)[0]
                self.undo_move(move)

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:  # Minimizing player (opponent)
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_possible_moves(self.opponent):
                self.perform_move(move)
                eval = self.minimax(depth - 1, alpha, beta, True, move)[0]
                self.undo_move(move)

                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def is_terminal_node(self):
        return self.board.player_a.won or self.board.player_b.won

    def evaluate_board(self):
        score = 0

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

        # Je kürzer die Distanz, desto höher der Score
        score -= player_a_dist
        score += player_b_dist

        # Berücksichtige verbleibende Blockelemente
        score -= self.board.player_a.blocks

        return score

    def get_all_possible_moves(self, player):
        current_player = player

        # Überprüfe mögliche Bewegungen
        # mögliche nächste Züge
        possible_actions = []
        # mögliche Bewegungen erzeugen
        possible_moves = list(
            nx.neighbors(self.board.graph, f"{current_player.node['row']},{current_player.node['col']}"))
        if (current_player.node['row'] == 0):
            possible_moves.remove('Verbindung_zu_Reihe_0')
        elif (current_player.node['row'] == 8):
            possible_moves.remove('Verbindung_zu_Reihe_8')
        while {} in possible_moves:
            possible_moves.remove({})
        # mögliche Bewegungen zu möglichen Zügen hinzufügen
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

        # Füge mögliche Blockierungen hinzu
        if current_player.blocks > 0 and self.board.player_a.node != self.board.player_b.node:
            # Welcher Spieler blockiert? + Nachbarknoten des Gegners hinzufügen
            if current_player == self.board.player_b:
                blocking_nodes = list(nx.neighbors(self.board.graph,
                                                   f"{self.board.player_a.node['row']},{self.board.player_a.node['col']}"))

            else:
                blocking_nodes = list(nx.neighbors(self.board.graph,
                                                   f"{self.board.player_b.node['row']},{self.board.player_b.node['col']}"))

            if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
            if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

            # Nachbar-nachbar-Knoten hinzufügen
            neighbour_nodes = []
            for neighbour in blocking_nodes:
                for neighbour_node in nx.neighbors(self.board.graph,
                                                   f"{neighbour.split(',')[0]},{neighbour.split(',')[1]}"):
                    neighbour_nodes.append(neighbour_node)
            for neighbour in neighbour_nodes:
                if neighbour not in blocking_nodes and neighbour not in self.board.nodes_used_for_blocking:
                    blocking_nodes.append(neighbour)
            if 'Verbindung_zu_Reihe_0' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_0')
            if 'Verbindung_zu_Reihe_8' in blocking_nodes: blocking_nodes.remove('Verbindung_zu_Reihe_8')

            # zulässige ermittelte Knoten zu möglichen Zügen hinzufügen
            for node in blocking_nodes:
                if node not in self.board.nodes_used_for_blocking:
                    split_node = node.split(',')
                    if int(split_node[0]) != 8:
                        possible_actions.append(f"block {split_node[0]} {split_node[1]} horizontal")
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
        _, best_move = self.minimax(depth, float('-inf'), float('inf'), True, None)
        return best_move


if __name__ == "__main__":
    board = Board(9)
    minimax_search = MinimaxGameSearch(board, board.player_a)
    print(minimax_search.search_next_move(3))  # Stellen Sie sicher, dass die Tiefe Ihren Anforderungen entspricht.