#!/usr/bin/env python

"""Minimal Chess"""

__copyright__ = "Copyright 2007, Scott Forbes"
__license__ = "GPL"

import sys, string, re, copy


# piece valuations
valuation = {"P": 1, "B": 3, "N": 3, "R": 5, "Q": 10, "K": 1000}

# list of move directions (dx, dy, maxStep) for each linear-moving piece
# fmt: off
legalMoves = {
    "B": ((-1,-1, 8), (-1, 1, 8), ( 1,-1, 8), ( 1, 1, 8)),
    "R": ((-1, 0, 8), ( 0,-1, 8), ( 1, 0, 8), ( 0, 1, 8)),
    "Q": ((-1,-1, 8), (-1, 1, 8), ( 1,-1, 8), ( 1, 1, 8),
          (-1, 0, 8), ( 0,-1, 8), ( 1, 0, 8), ( 0, 1, 8)),
    "K": ((-1,-1, 1), (-1, 1, 1), ( 1,-1, 1), ( 1, 1, 1),
          (-1, 0, 1), ( 0,-1, 1), ( 1, 0, 1), ( 0, 1, 1)) }
# fmt: on


class Piece:
    """A chess piece."""

    def __init__(self, type, side):
        self.type = type
        self.side = side
        self.hasMoved = False


class Move:
    """A chess move of a piece, from (x1, y1) to (x2, y2)."""

    def __init__(self, piece=None, val=0, x2=None, y2=None):
        self.piece = piece
        self.val = val
        self.x2, self.y2 = x2, y2
        self.next = None


class Board:
    """A state of the chess board."""

    def __init__(self):
        self.pos = []
        for y1 in range(0, 8):
            self.pos.append(8 * [None])
        backRow = "RNBQKBNR"
        for i in range(0, 8):
            self.pos[0][i] = Piece(backRow[i], 1)
            self.pos[1][i] = Piece("P", 1)
            self.pos[6][i] = Piece("P", 0)
            self.pos[7][i] = Piece(backRow[i], 0)
        self.side = 0
        self.ply = 0

    def printRepr(self):
        print("     a  b  c  d  e  f  g  h")
        for y in range(7, -1, -1):
            print(y + 1, ":", end=" ")
            for x in range(0, 8):
                p = self.pos[y][x]
                if p:
                    if p.side:
                        s = f" {p.type} "
                    else:
                        s = f"{{{p.type}}}"
                else:
                    s = " . "
                sys.stdout.write(s)
            print()
        print()

    def findBestMove(self):
        """Find and return the best move for current side."""

        # copy board
        b2 = copy.copy(self)

        # set up search for our turn
        b2.ply = self.ply + 1
        b2.side = 1 - self.side
        b2.bestMove = Move(None, -9999)

        # for each of X's pieces on board
        for b2.y1 in range(0, 8):
            for b2.x1 in range(0, 8):
                # lift piece from starting position (x1, y1)
                piece = b2.pos[b2.y1][b2.x1]
                b2.pos[b2.y1][b2.x1] = None
                if piece and piece.side == self.side:
                    # for each possible move of piece, search for best next move
                    b2.piece = piece
                    pType = piece.type
                    b2.pRepr = repr(b2.piece)

                    if pType == "P":  # pawn:
                        if piece.side:
                            adv = 1
                        else:
                            adv = -1
                        move1Ok = b2.checkMoves(((0, adv),), canCapture=False)
                        if not piece.hasMoved and move1Ok:
                            b2.checkMoves(((0, 2 * adv),), canCapture=False)
                        b2.checkMoves(((1, adv), (-1, adv)), canMove=False)

                    elif pType == "N":  # knight:
                        # fmt: off
                        b2.checkMoves(((-1, -2), (-2, -1), ( 1, -2), ( 2, -1),
                                       ( 1,  2), ( 2,  1), (-1,  2), (-2,  1)))
                        # fmt: on

                    else:  # standard piece: try all legal moves for it
                        b2.findBestMoveLinearly()

                # restore original position of our piece
                b2.pos[b2.y1][b2.x1] = piece

        # return best move and its value
        return b2.bestMove

    def checkMoves(self, posList, canCapture=True, canMove=True):
        """Check all moves from (x1, y1) to positions in posList. Updates self.bestMove."""

        for dx, dy in posList:
            self.checkMove(self.x1 + dx, self.y1 + dy, canCapture, canMove)

    def findBestMoveLinearly(self):
        """Find the best move for standard piece at (x1, y1). Updates self.bestMove."""

        for dx, dy, maxDist in legalMoves[self.piece.type]:
            # move starts with self.piece at (x1, y1)
            x2, y2 = self.x1, self.y1
            while maxDist > 0:
                x2 += dx
                y2 += dy
                if not self.checkMove(x2, y2, True, True):
                    break
                maxDist -= 1

    def checkMove(self, x2, y2, canCapture, canMove):
        """Check a single move of piece at (x1, y1) to (x2, y2). Updates self.bestMove
        and returns True if successful."""

        # stop when we run off of board
        if x2 < 0 or y2 < 0 or x2 >= 8 or y2 >= 8:
            return False
        m = Move(self.piece, 0, x2, y2)
        m.x1, m.y1 = self.x1, self.y1
        piece2 = self.pos[y2][x2]

        if piece2:
            if canCapture and piece2.side == self.side:
                # if move is a capture: move value = piece value
                m.val = valuation[piece2.type]
            else:
                # stop if we run into our own piece
                return False

        elif not canMove:
            return False

        # if not at deepest ply level:
        if self.ply < 4:
            # make our actual move
            origHasMoved = self.piece.hasMoved
            self.piece.hasMoved = True
            self.pos[y2][x2] = self.piece

            # make move for other side on board copy
            m2 = self.findBestMove()

            # subtract that move value from our value
            m.val -= m2.val
            m.next = m2

            # remove our piece from this position
            self.pos[y2][x2] = piece2
            self.piece.hasMoved = origHasMoved

        # add in board position value (center is best)
        m.val += 0.8 - (abs(3.5 - x2) + abs(3.5 - y2)) * 0.1

        # only keep move if best
        if m.val > self.bestMove.val:
            self.bestMove = m
        return not piece2

    def move(self, m):
        """Actually make move m."""

        self.pos[m.y2][m.x2] = self.pos[m.y1][m.x1]
        self.pos[m.y1][m.x1] = None


if __name__ == "__main__":
    b = Board()
    testMode = 0

    # if given a starting-position-pattern filename, read in that file
    if len(sys.argv) == 2:
        if sys.argv[1] == "-t":
            testMode = 1
        else:
            pos = []
            for line in open(sys.argv[1]):
                bdLine = re.match(r" *[1-8]:(.*)", line)
                if bdLine:
                    row = []
                    for pType in re.findall(r"{*[A-Z.]}*", bdLine.group(1)):
                        if pType == ".":
                            row.append(None)
                        else:
                            side = 1
                            if pType[0] == "{":
                                side = 0
                                pType = pType[1]
                            row.append(Piece(pType, side))
                    pos.append(row)
            pos.reverse()
            b.pos = pos

    while 1:
        b.printRepr()

        # ask human for a move and check it for basic validity
        while 1:
            print("Your move:", end=" ")
            sys.stdout.flush()
            hIn = "a2 a4"
            if testMode:
                print(hIn)
            else:
                hIn = input()
            cmd = re.match(r"([a-h])([1-8])[^a-h1-8]+([a-h])([1-8])", hIn)
            if cmd:
                x1, y1 = ord(cmd.group(1)) - ord("a"), int(cmd.group(2)) - 1
                x2, y2 = ord(cmd.group(3)) - ord("a"), int(cmd.group(4)) - 1
                hPiece = b.pos[y1][x1]
                if not hPiece or hPiece.side != 1:
                    print(f"Not your piece at {chr(97+x1)}{y1+1}")
                    continue
                hMove = Move(x2=x2, y2=y2)
                hMove.x1, hMove.y1 = x1, y1
                b.move(hMove)
                break
            print("? Expected a pair of coordinates")
        b.printRepr()

        # computer's turn:
        m = b.findBestMove()
        b.move(m)

        if testMode:
            b.printRepr()
            break
