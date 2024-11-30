
import networkx as nx

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

        #Kanten erzeugen
        for row in range(self.size):
            for col in range(self.size):
                if(f'{row + 1},{col}'  in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row + 1},{col}')
                if (f'{row},{col + 1}' in self.graph.nodes):
                    self.graph.add_edge(f'{row},{col}', f'{row},{col + 1}')
        #Spieler erzeugen
        self.player_a = Player(self,0,4,'A')
        self.player_b = Player(self,8,4,'B')

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

    #TODO: Simulation eines Spieles implementieren
    # zunächst manuell steuerbar, dann per programmierter KI
    #def simulate_game(self):







class Player:
    def __init__(self, board, row, col, name):
        '''
        Player repräsentiert einen der beiden Spieler auf dem Spielfeld
        :param board: Das Spielfeld, auf welchem gespielt wird
        :param row: Startposition, Zeile
        :param col: Startposition, Spalte
        :param name: Symbol des Spielers (für die grafische Spielfeld ausgabe in der Konsole)
        '''
        self.board = board
        self.name = name
        self.node = board.graph.nodes.get(f'{row},{col}')
        self.node['symbol'] = self.name
        self.blocks = 10
        self.won = False
        if (row == 0):
            self.goal = 8
        if (row == 8):
            self.goal = 0

    def game_won(self):
        '''
        Falls ein Spieler seine ZielReihe erreischt hat, wird die Klassenvariable self.won auf True gesetzt
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
        if((direction == 'right')
                and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"]},{self.node["col"] + 1}') in self.board.graph.edges): #String zur Identifikation der Kante prüfen
            next_node = board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] + 1}')
            moved = True
        elif((direction == 'left')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"]},{self.node["col"] - 1}') in self.board.graph.edges):
            next_node = board.graph.nodes.get(f'{self.node["row"]},{self.node["col"] - 1}')
            moved = True
        elif((direction == 'up')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"] - 1},{self.node["col"]}') in self.board.graph.edges):
            next_node = board.graph.nodes.get(f'{self.node["row"] - 1},{self.node["col"]}')
            moved = True
        elif((direction == 'down')
             and (f'{self.node["row"]},{self.node["col"]}',f'{self.node["row"] + 1},{self.node["col"]}') in self.board.graph.edges):
            next_node = board.graph.nodes.get(f'{self.node["row"] + 1},{self.node["col"]}')
            moved = True

        if(moved):
            self.node['symbol'] = '□' #altes Feld bekommt Symbol für leeres Feld zugewiesen
            self.node = next_node #Spielerfeld wird aktualisiert
            self.node['symbol'] = self.name #neues Feld bekommt Symbol vom Spieler
            self.game_won() #Prüfung, ob das Spiel gewonnen wurde
        if((moved is False) or #Bewegung war ungültig
                (moved is True and self.name == 'A' and self.node == board.player_b.node) # oder Spieler A springt über Spieler B
                or (moved is True and self.name == 'B' and self.node == board.player_a.node)): #oder Spieler B springt über Spieler A
            return False
        return True #Bewegung war gültig und der Spieler springt nicht über den anderen

    def place_blocking_element(self, row, col, orientation):
        '''
        Plazieren einer Blockade auf dem Spielfeld,
            Näheres in der Klasse Blocking_element
        :param row: Ausgangszeile der Blockade
        :param col: Ausgangsspalte der Blockade
        :param orientation: orientierung der Blockade ('vertical' oder 'horizontal')
        :return: Falls Blockade plaziert werden konnte:
                    True
                sonst (eine oder beide der Kanten sind schon blockiert):
                    False
        '''
        blocking_element = Blocking_element(self, row, col, orientation)
        edge_a, edge_b = blocking_element.return_blocked_paths()
        if (edge_a in self.board.graph.edges
            and edge_b in self.board.graph.edges):
            self.board.graph.remove_edge(edge_a[0], edge_a[1])
            self.board.graph.remove_edge(edge_b[0], edge_b[1])
            self.blocks -= 1
            return True
        return False

        #TODO Blockierende elemente dürfen sich nicht überlappen


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
    board.graph.remove_edge(f'{4},{4}', f'{5},{4}')
    board.player_b.place_blocking_element(7,3,'horizontal')
    board.player_b.move('right')
    board.player_b.move('right')
    board.player_b.move('right')
    board.player_b.move('right')
    board.player_b.move('up')
    board.player_a.move('down')
    board.player_a.move('down')
    board.player_a.move('down')
    board.player_a.move('down')
    board.player_a.move('down')# wird nicht gemacht, da Kante fehlt
    board.player_a.move('down')# wird nicht gemacht, da Kante fehlt
    board.player_a.move('down')# wird nicht gemacht, da Kante fehlt
    board.player_a.move('down')# wird nicht gemacht, da Kante fehlt
    board.player_a.move('left')
    board.player_a.move('down')
    board.player_a.move('down')
    board.player_a.move('down')
    board.player_a.move('down')# wird nicht gemacht, da Kante fehlt
    board.print_board()

