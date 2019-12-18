import math
from copy import deepcopy
import logging
import random
import copy
import json


class Player:
    """ Skeleton for human and agent player """

    def play(self, *board):
        pass

    def receiveReward(self, reward):
        pass


class HumanPlayer(Player):
    def play(self, board):
        try:
            while True:
                print("Entrer un entier entre 0 et 2 pour x")
                x = int(input())
                print("Entrer un entier entre 0 et 2 pour y")
                y = int(input())
                # no cheat
                if (x > -1 and x < 3) and (y > -1 and y < 3) and board[x][y] == " ":
                    return x, y
        except:
            print('Saisir de bonne valeur')
            return self.play(board)


class Agent(Player):
    def __init__(self, learning_factor, refresh_factor, file_name):

        self.filename = file_name

        try:
            with open(self.filename) as json_file:
                data_loaded = json.load(json_file)

            if len(data_loaded) == 0:
                data_loaded = {}

        except:
            data_loaded = {}

        self.data_loaded = data_loaded

        self.learning_factor = learning_factor
        self.refresh_factor = refresh_factor
        self.history = []

        # self.learning_factor = 0.5 if self.learning_factor >= 1 or self.learning_factor <= 0 else print("potato")
        # self.refresh_factor = 0.5 if self.refresh_factor >= 1 or self.refresh_factor  <= 0 else print("potato")

    def play(self, board, current_player):
        available_pos = self.findAvailablePositions(board)
        current_best = [None, None]
        current_int = 0
        undefined_found = False
        undefined_pos = []

        for i in range(0, len(available_pos)):
            tmp_board = copy.deepcopy(board)
            tmp_board[available_pos[i][0]][available_pos[i][1]] = current_player

            if str(tmp_board) in self.data_loaded:
                if self.data_loaded[str(tmp_board)] > current_int:
                    current_int = self.data_loaded[str(tmp_board)]
                    current_best = available_pos[i]
            else:
                undefined_found = True
                undefined_pos.append(available_pos[i])

        if undefined_found:
            random_value = random.randint(0, len(undefined_pos) - 1)
            choose_pos = undefined_pos[random_value]
        elif current_best == [None, None]:
            random_value = random.randint(0, len(available_pos) - 1)
            choose_pos = available_pos[random_value]
        else:
            choose_pos = current_best

        tmp_board = copy.deepcopy(board)

        tmp_board[choose_pos[0]][choose_pos[1]] = current_player
        self.history.append(str(tmp_board))

        return choose_pos[0], choose_pos[1]

    def receiveReward(self, reward):

        try:
            values = self.data_loaded.values()
            maxValue = max(values)
        except:
            maxValue = reward

        for i in range(0, len(self.history)):
            if self.history[i] in self.data_loaded:
                tmp_value = copy.deepcopy(self.data_loaded[self.history[i]])
                self.data_loaded[self.history[i]] = \
                    tmp_value + \
                    self.learning_factor * (
                        reward + self.refresh_factor * maxValue - tmp_value)
            else:
                self.data_loaded[self.history[i]] = reward

        with open(self.filename, 'w') as outfile:
            json.dump(self.data_loaded, outfile)

    def findAvailablePositions(self, board):
        available_positions = []
        for i in range(0, len(board)):
            for j in range(0, len(board[i])):
                if board[i][j] == ' ':
                    available_positions.append([i, j])

        return available_positions


class Environment:
    def __init__(self, player1, player2, withHuman=False):
        self.board = []
        self.player1 = player1
        self.player2 = player2
        self.canPlay = True
        self.playerWinner = ''
        self.withHuman = withHuman
        self.player1_win_count = 0
        self.player2_win_count = 0
        self.draw_count = 0

    def initGame(self):
        """  Defines a bard with 9 empty case, ie a space
            and indicates if a player can play
        """
        self.board = [[' ' for i in range(3)] for j in range(3)]
        self.canPlay = True
        self.playerWinner = ''

    def launchGame(self, game_count):
        """ Alternate the move between the two player """
        self.initGame()
        currentPlayer = 'X' if game_count % 2 == 0 else 'O'
        continueGame = True

        while continueGame:
            # print for human
            if self.withHuman:
                print(self)
            if currentPlayer == 'X':
                x, y = self.player1.play(self.board, currentPlayer)
                self.board[x][y] = currentPlayer
                currentPlayer = 'O'
            else:
                x, y = self.player2.play(self.board, currentPlayer)
                self.board[x][y] = currentPlayer
                currentPlayer = 'X'
            # TO DO give the new state to agents
            if self.winner() or not self.playerCanPlay():
                if self.withHuman:
                    print(self)
                logging.info('*** End game *** \n' + self.__str__())
                if self.playerWinner != '':
                    if self.withHuman:
                        print(self.playerWinner, 'win')
                    logging.info('winner is ' + self.playerWinner)
                else:
                    if self.withHuman:
                        print('null game')
                    logging.info('null game')
                continueGame = False
                self.giveRewards()

    def winner(self):
        """ Returns True if a winner exists or False
        """
        # check the rows
        for i in range(3):
            if self.board[i][0] == self.board[i][1] and self.board[i][0] == self.board[i][2] and self.board[i][
                0] != " ":
                self.playerWinner = self.board[i][0]
                return True
        # check the colunms
        for i in range(3):
            if self.board[0][i] == self.board[1][i] and self.board[0][i] == self.board[2][i] and self.board[0][
                i] != " ":
                self.playerWinner = self.board[0][i]
                return True
        # check diagonales
        if self.board[0][0] == self.board[1][1] and self.board[0][0] == self.board[2][2] and self.board[0][0] != " ":
            self.playerWinner = self.board[i][0]
            return True
        if self.board[0][2] == self.board[1][1] and self.board[0][2] == self.board[2][0] and self.board[0][2] != " ":
            self.playerWinner = self.board[i][0]
            return True
        return False

    def playerCanPlay(self):
        """ Use to determine null game """
        for row in self.board:
            if row.count(' ') > 0:
                return True
        return False

    def giveRewards(self):
        print(self.playerWinner)
        if self.playerWinner.upper() == 'X':
            self.player1_win_count += 1
            self.player1.receiveReward(1)
            self.player2.receiveReward(0)
        elif self.playerWinner.upper() == 'O':
            self.player2_win_count += 1
            self.player2.receiveReward(1)
            self.player1.receiveReward(0)
        else:
            self.draw_count += 1
            self.player1.receiveReward(0.5)
            self.player2.receiveReward(0.5)

        print(self.__str__())
        print('AGENT 1 WINS : ' + str(self.player1_win_count))
        print('AGENT 2 WINS : ' + str(self.player2_win_count))
        print('DRAW : ' + str(self.draw_count))

    def __str__(self):
        s = ''
        for i in range(3):
            s += "|"
            for j in range(3):
                s += self.board[i][j] + "|"
            s += '\n'
        return s


if __name__ == '__main__':
    print('*** TRAININ PERIOD ***')
    # # to log each action of agent
    # logging.basicConfig(self.filename='game.log', level=logging.DEBUG)

    agent1 = Agent(0.42, 0.33, "fileSave1.json")
    agent2 = Agent(0.42, 0.33, "fileSave2.json")
    game = Environment(agent1, agent2)
    for i in range(0, 200000):
        print("Turn {} of training".format(i))
        game.launchGame(i)
    # play with the agent
    # print(" Let's go now !!! ")
    # continuePlay = 'y'
    # human = HumanPlayer()
    # game = Environment(agent1, human, True)
    # while continuePlay == 'y':
    #     game.launchGame()
    #     continuePlay = input('Again?(y/n)')
