import networkx as nx
from src.ki.monte_carlo_game_search import *


class Board:
    '''
    Die Klasse Board repräsentiert das Spielfeld des Spiels Quoridor
    '''
    def __init__(self, size):
        '''
        Das Spielfeld wird als Graph angelegt, auf Basis der Library networkx
        Zur Darstellung der Knoten und Kanten:
            ein Knoten wird über einen String 'row,col' identifiziert
            Knoten enthalten als Attribute ihre Reihe und Zeile und ihr aktuelles Symbol
            eine Kante wird über ein Tupel (node_a,node_b) identifiziert
        :param size: Spielfeldgröße == size x size
        '''
        self.graph = nx.Graph()
        self.size = size
        #Knoten erzeugen
        for row in range(self.size):
            for col in range(self.size):
                self.graph.add_node(f'{row},{col}',row = row, col = col, symbol = '□')
        #Knoten für Wegfindung
        self.graph.add_node('Verbindung_zu_Reihe_0')
        self.graph.add_node('Verbindung_zu_Reihe_8')

        #Kanten erzeugen
        for row in range(self.size):
            for col in range(self.size):
                if(f'{row + 1},{col}'  in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row + 1},{col}')
                if (f'{row},{col + 1}' in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row},{col + 1}')

        #Kanten für Wegfindung
        for col in range(self.size):
            self.graph.add_edge('Verbindung_zu_Reihe_0', f'{0},{col}')
            self.graph.add_edge('Verbindung_zu_Reihe_8', f'{8},{col}')

        #Spieler erzeugen
        self.player_a = Player(self,0,4,'A','monte_carlo_game_search')
        self.player_b = Player(self,8,4,'B','monte_carlo_game_search')
        self.nodes_used_for_blocking = []

    def copy(self):
        new_board = Board(self.size)
        new_board.graph = self.graph.copy()
        new_board.nodes_used_for_blocking = self.nodes_used_for_blocking.copy()
        new_board.player_a = self.player_a.copy(new_board)
        new_board.player_b = self.player_b.copy(new_board)
        return new_board


    def print_board(self):
        '''
        grafische Ausgabe des Spielfeldes auf der Konsole
        :return:
        '''
        for row in range(self.size):
            for col in range(self.size):
                print(self.graph.nodes.get(f'{row},{col}').get('symbol'), end='')
                print('  ', end='')
                if((f'{row},{col}', f'{row},{col + 1}') in self.graph.edges):
                    print('———', end ='')
                else:
                    print('   ', end='')
                print('  ', end='')
            print()
            for col in range(self.size):
                if((f'{row},{col}', f'{row + 1},{col}') in self.graph.edges):
                    print('|', end ='')
                else:
                    print(' ', end='')
                print('       ', end='')
            print()

    # Simulation eines Spieles implementieren
    # zunächst manuell steuerbar (Konsole), dann per programmierter KI

    def simulate_game(self):
        current_player = self.player_a
        while not self.player_a.won and not self.player_b.won:
            self.print_board()
            print(f"Spieler {current_player.name} ist am Zug.")

            if(current_player.ai == 'manuell'):
                #Wenn der aktive Spieler über den Anderen springt
                if self.player_a.node == self.player_b.node:
                    blocking_invalid = True
                    action = input("Sie sind im Sprung über den anderen Spieler, in welcher Richtung möchten sie landen?: (move [direction]): ")
                #Wenn der aktive Spieler nicht über den Anderen springt (Regelfall)
                else:
                    blocking_invalid = False
                    action = input("Wählen Sie eine Aktion: (move [direction] oder block [row] [col] [orientation]): ")
            elif(current_player.ai == 'monte_carlo_game_search'):
                if self.player_a.node == self.player_b.node:
                    blocking_invalid = True
                else:
                    blocking_invalid = False
                monte_carlo_game_search = Monte_carlo_game_search(self, current_player)
                action = monte_carlo_game_search.search_next_move(100)
            action_parts = action.split()

            move_ok = True
            #Prüfen des move Befehls
            if action_parts[0] == 'move' and len(action_parts) == 2:
                direction = action_parts[1]
                if not current_player.move(direction):
                    move_ok = False
                    print("Ungültiger Zug, bitte erneut versuchen.")

            #Prüfen des block Befehls
            elif action_parts[0] == 'block' and len(action_parts) == 4:
                if blocking_invalid:
                    print("Blockieren ist nicht erlaubt, da Sie über den Gegner springen.")
                    continue  # Gehe zurück zur Eingabeaufforderung
                row, col, orientation = int(action_parts[1]), int(action_parts[2]), action_parts[3]
                if not current_player.place_blocking_element(row, col, orientation):
                    print("Blockade konnte nicht platziert werden, bitte erneut versuchen.")
                    move_ok = False

            else:
                move_ok = False
                print(
                    "Ungültige Aktion. Bitte verwenden Sie 'move [direction]' oder 'block [row] [col] [orientation]'.")

            #Wechsel des Spielers oder nochmal, falls Spielzug ungültig
            if move_ok:
                current_player = self.player_b if current_player == self.player_a else self.player_a

            #Falls ein Spieler gerade über den anderen springt
            if blocking_invalid:
                #Falls der Sprung geklappt hat (aktualisierung der Symbole zur richtigen Darstellung)
                if not self.player_a.node == self.player_b.node:
                    self.player_b.node['symbol'] = 'B'
                    self.player_a.node['symbol'] = 'A'
            self.player_b.node['symbol'] = 'B'
            self.player_a.node['symbol'] = 'A'

        #Spiel beendet, Ausgabe des Gewinners
        self.print_board()
        if self.player_a.won:
            print("Spieler A hat gewonnen!")
        else:
            print("Spieler B hat gewonnen!")

class Player:
    def __init__(self, board, row, col, name, ai):
        '''
        Player repräsentiert einen der beiden Spieler auf dem Spielfeld
        :param board: Das Spielfeld, auf welchem gespielt wird
        :param row: Startposition, Zeile
        :param col: Startposition, Spalte
        :param name: Symbol des Spielers (für die grafische Spielfeldausgabe in der Konsole)
        '''
        self.board = board
        self.name = name
        self.node = board.graph.nodes.get(f'{row},{col}')
        self.node['symbol'] = self.name
        self.blocks = 10
        self.won = False
        self.row = -1
        self.ai = ai

        if (row == 0):
            self.goal = 8
        if (row == 8):
            self.goal = 0

    def copy(self, board):
        new_player = Player(board,self.node['row'],self.node['col'],self.name,self.ai)
        new_player.goal = self.goal
        new_player.blocks = self.blocks
        new_player.won = False
        return new_player

    def game_won(self):
        '''
        Falls ein Spieler seine ZielReihe erreicht hat, wird die Klassenvariable self.won auf True gesetzt
        '''
        if(self.node['row'] == self.goal):
            self.won = True


    def move(self, direction):
        '''
        Bewegung eines Spielers auf dem Spielfeld
        :param direction: Richtung in welche der Spieler sich bewegen will
        :return: Falls die Bewegung ungültig ist (außerhalb des Felder oder keine Verbindung zwischen 2 positionen, nach der Bewegung)
                    oder der Spieler auf dem anderen Spieler steht (nach der Bewegung):
                    False
                sonst:
                    True
        '''
        moved = False #hat der Spieler sich bewegt?
        next_node = self.node
        if((direction == 'right')
                and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"]},{self.node["col"] + 1}') in self.board.graph.edges): #String zur Identifikation der Kante prüfen
            next_node = self.board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] + 1}')
            moved = True
        elif((direction == 'left')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"]},{self.node["col"] - 1}') in self.board.graph.edges):
            next_node = self.board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] - 1}')
            moved = True
        elif((direction == 'up')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"] - 1},{self.node["col"]}') in self.board.graph.edges):
            next_node = self.board.graph.nodes.get(f'{self.node["row"] - 1},{self.node["col"]}')
            moved = True
        elif((direction == 'down')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"] + 1},{self.node["col"]}') in self.board.graph.edges):
            next_node = self.board.graph.nodes.get(f'{self.node["row"] + 1},{self.node["col"]}')
            moved = True

        if(moved):
            self.node['symbol'] = '□' #altes Feld bekommt Symbol für leeres Feld zugewiesen
            self.node = next_node #Spielerfeld wird aktualisiert
            self.node['symbol'] = self.name #neues Feld bekommt Symbol vom Spieler
            self.game_won() #Prüfung, ob das Spiel gewonnen wurde
        if((moved is False) or #Bewegung war ungültig
                (moved is True and self.name == 'A' and self.node == self.board.player_b.node) # oder Spieler A springt über Spieler B
                or (moved is True and self.name == 'B' and self.node == self.board.player_a.node)): #oder Spieler B springt über Spieler A
            return False
        return True #Bewegung war gültig und der Spieler springt nicht über den anderen

    def place_blocking_element(self, row, col, orientation):
        '''
        Platzieren einer Blockade auf dem Spielfeld,
            Näheres in der Klasse Blocking_element
        :param row: Ausgangszeile der Blockade
        :param col: Ausgangsspalte der Blockade
        :param orientation: orientierung der Blockade ('vertical' oder 'horizontal')
        :return: Falls Blockade platziert werden konnte:
                    True
                sonst (eine oder beide der Kanten sind schon blockiert):
                    False
        '''
        blocking_element = Blocking_element(self, row, col, orientation)
        edge_a, edge_b = blocking_element.return_blocked_paths()
        if (edge_a in self.board.graph.edges
            and edge_b in self.board.graph.edges
            and f'{row},{col}' not in self.board.nodes_used_for_blocking):
            self.board.graph.remove_edge(edge_a[0], edge_a[1])
            self.board.graph.remove_edge(edge_b[0], edge_b[1])
            if (not self.check_if_path_exists()):
                self.board.graph.add_edge(edge_a[0], edge_a[1])
                self.board.graph.add_edge(edge_b[0], edge_b[1])
                return False
            self.blocks -= 1
            self.board.nodes_used_for_blocking.append(f'{row},{col}')
            return True
        return False

    def check_if_path_exists(self):
        path_player_a_exists = False
        path_player_b_exists = False
        graph_for_player_a = self.board.graph.copy()
        graph_for_player_a.remove_node('Verbindung_zu_Reihe_0')
        graph_for_player_b = self.board.graph.copy()
        graph_for_player_b.remove_node('Verbindung_zu_Reihe_8')
        #check for both players, if any path to a tile of the goal row exists
        if nx.has_path(graph_for_player_a,f'{self.board.player_a.node["row"]},{self.board.player_a.node["col"]}','Verbindung_zu_Reihe_8'):
            path_player_a_exists = True
        if nx.has_path(graph_for_player_b,f'{self.board.player_b.node["row"]},{self.board.player_b.node["col"]}','Verbindung_zu_Reihe_0'):
            path_player_b_exists = True
        if path_player_a_exists and path_player_b_exists:
            return True
        return False


class Blocking_element:
    def __init__(self, board, row, col, orientation):
        '''
                Spielteil zum Blockieren des Weges
                in dem folgenden Beispiel zur Auswirkung von direction
                hat 'a' die Position [row,col]

                Die Knoten stehen wie folgt zueinander:

                    a-----b
                    |     |
                    c-----d

                wenn orientation == horizontal:
                    die Verbindungen (Kanten) zwischen a und c (bzw. b und d) sind blockiert (gelöscht)

                    a-----b

                    c-----d

                wenn orientation == vertical:
                    die Verbindungen (Kanten) zwischen a und b (bzw. c und d) sind blockiert (gelöscht)

                    a     b
                    |     |
                    c     d

                :param row: row-Position von a
                :param col: col-Position von a
                :param orientation: Ausrichtung des blockierenden Elementes
                :param board: Spielfeld
                '''
        self.row = row
        self.col = col
        self.orientation = orientation
        self.board = board

        self.pos_a = f'{row},{col}'
        self.pos_b = f'{row + 1},{col}'
        self.pos_c = f'{row},{col + 1}'
        self.pos_d = f'{row + 1},{col + 1}'

    def return_blocked_paths(self):
        '''
        Rückgabe der beiden blockierten Kanten,
        je nach Ausrichtung
        :return: Kante a, Kante b
        '''
        if self.orientation == 'horizontal':
            edge_a = (self.pos_a,self.pos_b)
            edge_b = (self.pos_c,self.pos_d)
            return edge_a,edge_b
        elif self.orientation == 'vertical':
            edge_a = (self.pos_a,self.pos_c)
            edge_b = (self.pos_b,self.pos_d)
            return edge_a,edge_b



if __name__ == '__main__':
    #Ein paar beispielhafte Züge und wie das Spielfeld danach aussieht
    board = Board(9)
    board.simulate_game()

