## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports

# PySol imports
from mfxutil import Struct
from pysoltk import MfxCanvasText
from resource import CSI


# /***********************************************************************
# // a helper class to create common layouts
# ************************************************************************/

# a layout stack
class _LayoutStack:
    def __init__(self, x, y, suit=None):
        self.x = int(round(x))
        self.y = int(round(y))
        self.suit = suit
        self.text_args = {}
        self.text_format = "%d"

    def setText(self, x, y, anchor="center", format=None, **kw):
        self.text_args["x"] = x
        self.text_args["y"] = y
        self.text_args["anchor"] = anchor
        self.text_args.update(kw)
        if format is not None:
            self.text_format = format


class Layout:
    def __init__(self, game, card_x_space=None, card_y_space=None, **kw):
        self.game = game
        self.canvas = self.game.canvas
        self.size = None
        self.s = Struct(
            talon = None,
            waste = None,
            foundations = [],
            rows = [],
            reserves = [],
        )
        self.stackmap = {}
        self.regions = []
        # set visual constants
        images = self.game.app.images
        cardset_size = images.cs.si.size
        if cardset_size in (CSI.SIZE_TINY, CSI.SIZE_SMALL):
            layout_x_margin = 6
            layout_y_margin = 6
            layout_card_x_space = 6
            layout_card_y_space = 10
        elif cardset_size in (CSI.SIZE_MEDIUM,):
            layout_x_margin = 8
            layout_y_margin = 8
            layout_card_x_space = 8
            layout_card_y_space = 12
        else:  # CSI.SIZE_LARGE, CSI.SIZE_XLARGE
            layout_x_margin = 10
            layout_y_margin = 10
            layout_card_x_space = 10
            layout_card_y_space = 14

        self.CW = images.CARDW
        self.CH = images.CARDH
        self.XOFFSET = images.CARD_XOFFSET
        self.YOFFSET = images.CARD_YOFFSET

        self.XM = layout_x_margin                   # XMARGIN
        self.YM = layout_y_margin                   # YMARGIN


        if card_x_space is None:
            self.XS = self.CW + layout_card_x_space          # XSPACE
        else:
            self.XS = self.CW + card_x_space
        if card_y_space is None:
            self.YS = self.CH + layout_card_y_space          # YSPACE
        else:
            self.YS = self.CH + card_y_space

        ##self.CARD_X_SPACE = layout_card_x_space
        ##self.CARD_Y_SPACE = layout_card_y_space
        ##self.RIGHT_MARGIN = layout_x_margin-layout_card_x_space
        ##self.BOTTOM_MARGIN = layout_y_margin-layout_card_y_space

        font = game.app.getFont("canvas_default")
        ##self.TEXT_MARGIN = 10
        self.TEXT_MARGIN = font[1]
        ##self.TEXT_HEIGHT = 30
        self.TEXT_HEIGHT = 18+font[1]

        self.__dict__.update(kw)
        if self.game.preview > 1:
            if "XOFFSET" in kw:
                self.XOFFSET =  self.XOFFSET / self.game.preview
            if "YOFFSET" in kw:
                self.YOFFSET =  self.YOFFSET / self.game.preview
            self.TEXT_HEIGHT = 10

    def __createStack(self, x, y, suit=None):
        stack = _LayoutStack(x, y, suit)
        mapkey = (stack.x, stack.y)
        #from pprint import pprint
        #print mapkey
        #pprint(self.stackmap)
        assert mapkey not in self.stackmap
        self.stackmap[mapkey] = stack
        return stack

    def _setText(self, stack, anchor="center"):
        tx, ty, ta, tf = self.getTextAttr(stack, anchor)
        stack.setText(tx, ty, ta, tf)

    #
    #
    #

    def createGame(self, layout_method,
                   talon_class=None,
                   waste_class=None,
                   foundation_class=None,
                   row_class=None,
                   reserve_class=None,
                   **kw
                   ):
        # create layout
        game = self.game
        s = game.s
        layout_method(self, **kw)
        game.setSize(self.size[0], self.size[1])
        # create stacks
        if talon_class:
            s.talon = talon_class(self.s.talon.x, self.s.talon.y, game)
        if waste_class:
            s.waste = waste_class(self.s.waste.x, self.s.waste.y, game)
        if foundation_class:
            if isinstance(foundation_class, (list, tuple)):
                n = len(self.s.foundations)/len(foundation_class)
                i = 0
                for j in range(n):
                    for cls in foundation_class:
                        r = self.s.foundations[i]
                        s.foundations.append(cls(r.x, r.y, game, suit=r.suit))
                        i += 1

            else:
                for r in self.s.foundations:
                    s.foundations.append(foundation_class(r.x, r.y, game,
                                                          suit=r.suit))
        if row_class:
            for r in self.s.rows:
                s.rows.append(row_class(r.x, r.y, game))
        if reserve_class:
            for r in self.s.reserves:
                s.reserves.append(reserve_class(r.x, r.y, game))
        # default
        self.defaultAll()

    #
    # public util for use by class Game
    #

    def getTextAttr(self, stack, anchor):
        x, y = 0, 0
        delta_x, delta_y = 4, 4
        delta_yy = 10
        if stack is not None:
            x, y = stack.x, stack.y
        if anchor == "n":
            return (x+self.CW/2, y-delta_y, "s", "%d")
        if anchor == "nn":
            return (x+self.CW/2, y-delta_yy, "s", "%d")
        if anchor == "s":
            return (x+self.CW/2, y+self.CH+delta_y, "n", "%d")
        if anchor == "ss":
            return (x+self.CW/2, y+self.CH+delta_yy, "n", "%d")
        if anchor == "nw":
            return (x-delta_x, y, "ne", "%d")
        if anchor == "sw":
            return (x-delta_x, y+self.CH, "se", "%d")
        f = "%2d"
        if self.game.gameinfo.decks > 1:
            f = "%3d"
        if anchor == "ne":
            return (x+self.CW+delta_x, y, "nw", f)
        if anchor == "se":
            return (x+self.CW+delta_x, y+self.CH, "sw", f)
        if anchor == "e":
            return (x+self.CW+delta_x, y+self.CH/2, "w", f)
        raise ValueError(anchor)

    def createText(self, stack, anchor, dx=0, dy=0, text_format=""):
        if self.canvas.preview > 1:
            return
        assert stack.texts.ncards is None
        tx, ty, ta, tf = self.getTextAttr(stack, anchor)
        font = self.game.app.getFont("canvas_default")
        stack.texts.ncards = MfxCanvasText(self.canvas, tx+dx, ty+dy,
                                           anchor=ta, font=font)
        stack.texts.ncards.text_format = text_format or tf

    def setRegion(self, stacks, rects):
        self.regions.append((stacks, rects))


    #
    # util for use by a Game
    #

    def defaultAll(self):
        game = self.game
        # create texts
        if game.s.talon:
            game.s.talon.texts.ncards = self.defaultText(self.s.talon)
        if game.s.waste:
            game.s.waste.texts.ncards = self.defaultText(self.s.waste)
        # define stack-groups
        self.defaultStackGroups()
        # set regions
        self.defaultRegions()

    def defaultText(self, layout_stack):
        if self.canvas.preview > 1:
            return None
        ##print layout_stack, layout_stack.text_args
        if layout_stack is None or not layout_stack.text_args:
            return None
        layout_stack.text_args["font"] = self.game.app.getFont("canvas_default")
        t = apply(MfxCanvasText, (self.game.canvas,), layout_stack.text_args)
        t.text_format = layout_stack.text_format
        return t

    # define stack-groups
    def defaultStackGroups(self):
        game = self.game
        waste = []
        if game.s.waste is not None: waste = [game.s.waste]
        game.sg.talonstacks = [game.s.talon] + waste
        game.sg.dropstacks = game.s.rows + game.s.reserves + waste
        game.sg.openstacks = game.s.foundations + game.s.rows + game.s.reserves
        game.sg.reservestacks = game.s.reserves

    def defaultRegions(self):
        for region in self.regions:
            # convert layout-stacks to corresponding game-stacks
            stacks = []
            for s in region[0]:
                mapkey = (s.x, s.y)
                id = self.game.stackmap[mapkey]
                stacks.append(self.game.allstacks[id])
            ##print stacks, region[1]
            self.game.setRegion(stacks, region[1])


    #
    # Baker's Dozen layout
    #  - left: 2 rows
    #  - right: foundations, talon
    #

    def bakersDozenLayout(self, rows, texts=0, playcards=9):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)
        halfrows = (rows + 1) / 2

        # set size so that at least 9 cards are fully playable
        h = YS + min(2*YS, (playcards-1)*self.YOFFSET)
        h = max(h, 5*YS/2, 3*YS/2+CH)
        h = min(h, 3*YS)

        # create rows
        x, y = XM, YM
        for i in range(halfrows):
            self.s.rows.append(S(x+i*XS, y))
        for i in range(rows-halfrows):
            self.s.rows.append(S(x+i*XS, y+h))

        # create foundations
        x, y = XM + halfrows * XS, YM
        self.setRegion(self.s.rows, (-999, -999, x - CW / 2, 999999))
        for suit in range(suits):
            for i in range(decks):
                self.s.foundations.append(S(x+i*XS, y, suit=suit))
            y = y + YS

        # create talon
        h = YM + 2*h
        self.s.talon = s = S(x, h - YS)
        if texts:
            assert 0

        # set window
        self.size = (XM + (halfrows+decks)*XS, h)


    #
    # FreeCell layout
    #  - top: free cells, foundations
    #  - below: rows
    #  - left bottom: talon
    #

    def freeCellLayout(self, rows, reserves, texts=0, playcards=18):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)
        toprows = reserves + 1 + suits*decks
        maxrows = max(rows, toprows)

        w = XM + maxrows*XS

        # set size so that at least 2/3 of a card is visible with 18 cards
        h = CH*2/3 + (playcards-1)*self.YOFFSET
        h = YM + YS + max(h, 3*YS)

        # create reserves & foundations
        x, y = (w - (toprows*XS - XM))/2, YM
        for i in range(reserves):
            self.s.reserves.append(S(x, y))
            x = x + XS
        for suit in range(suits):
            for i in range(decks):
                x = x + XS
                self.s.foundations.append(S(x, y, suit=suit))

        # create rows
        x, y = (w - (rows*XS - XM))/2, YM + YS
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS
        self.setRegion(self.s.rows, (-999, y - CH / 2, 999999, 999999))

        # create talon
        x, y = XM, h - YS
        self.s.talon = s = S(x, y)
        if texts:
            # place text right of stack
            self._setText(s, anchor="se")

        # set window
        self.size = (w, h)


    #
    # Gypsy layout
    #  - left: rows
    #  - right: foundations, talon
    #  - bottom: reserves
    #

    def gypsyLayout(self, rows, waste=0, reserves=0, texts=1, playcards=25):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)

        if reserves:
            h = YS+(playcards-1)*self.YOFFSET+YS
        else:
            # set size so that at least 2/3 of a card is visible with 25 cards
            h = CH*2/3 + (playcards-1)*self.YOFFSET
        h = YM + max(h, (suits+1)*YS)

        # create rows
        x, y = XM, YM
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS
        self.setRegion(self.s.rows, (-999, -999, x - CW / 2, 999999))

        # create foundations
        for suit in range(suits):
            for i in range(decks):
                self.s.foundations.append(S(x+i*XS, y, suit=suit))
            y = y + YS

        # create talon and waste
        x, y = x + (decks-1)*XS, h - YS
        if texts:
            x = x - XS/2
        self.s.talon = s = S(x, y)
        if texts:
            # place text right of stack
            self._setText(s, anchor="se")
        if waste:
            x = x - XS
            self.s.waste = s = S(x, y)
            if texts:
                # place text left of stack
                self._setText(s, anchor="sw")
        # create reserves
        x, y = XM, h-YS
        for i in range(reserves):
            self.s.reserves.append(S(x, y))
            x += XS

        # set window
        self.size = (XM + (max(rows, reserves)+decks)*XS, h)


    #
    # Harp layout
    #  - top: rows
    #  - bottom: foundations, waste, talon
    #

    def harpLayout(self, rows, waste, texts=1, playcards=19):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)

        w = max(rows*XS, (suits*decks+waste+1)*XS, (suits*decks+1)*XS+2*XM)
        w = XM + w

        # set size so that at least 19 cards are fully playable
        h = YS + (playcards-1)*self.YOFFSET
        h = max(h, 3*YS)
        if texts: h += self.TEXT_HEIGHT

        # top
        x, y = (w - (rows*XS - XM))/2, YM
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS

        # bottom
        x, y = XM, YM + h
        self.setRegion(self.s.rows, (-999, -999, 999999, y - YS / 2))
        for suit in range(suits):
            for i in range(decks):
                self.s.foundations.append(S(x, y, suit=suit))
                x = x + XS
        if waste:
            x = w - 2*XS
            self.s.waste = s = S(x, y)
            if texts:
                # place text above stack
                self._setText(s, 'n')
        x = w - XS
        self.s.talon = s = S(x, y)
        if texts:
            # place text above stack
            self._setText(s, 'n')

        # set window
        self.size = (w, YM + h + YS)


    #
    # Klondike layout
    #  - top: talon, waste, foundations
    #  - bottom: rows
    #

    def klondikeLayout(self, rows, waste, texts=1, playcards=16, center=1, text_height=0):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)
        foundrows = 1 + (suits > 5)
        frows = decks * suits / foundrows
        toprows = 1 + waste + frows
        maxrows = max(rows, toprows)

        # set size so that at least 2/3 of a card is visible with 16 cards
        h = CH * 2 / 3 + (playcards - 1) * self.YOFFSET
        h = max(h, 2 * YS)

        # top
        ##text_height = 0
        x, y = XM, YM
        self.s.talon = s = S(x, y)
        if texts:
            if waste or not center or maxrows - frows <= 1:
                # place text below stack
                self._setText(s, 's')
                text_height = self.TEXT_HEIGHT
            else:
                # place text right of stack
                self._setText(s, 'ne')
        if waste:
            x = x + XS
            self.s.waste = s = S(x, y)
            if texts:
                # place text below stack
                self._setText(s, 's')
                text_height = self.TEXT_HEIGHT

        for row in range(foundrows):
            x = XM + (maxrows - frows) * XS
            if center and frows + 2 * (1 + waste + 1) <= maxrows:
                # center the foundations
                x = XM + (maxrows - frows) * XS / 2
            for suit in range(suits / foundrows):
                for i in range(decks):
                    self.s.foundations.append(S(x, y, suit=suit + (row * (suits / 2))))
                    x = x + XS
            y = y + YS

        # bottom
        x = XM
        if rows < maxrows: x += (maxrows-rows) * XS/2
        ##y += YM * (3 - foundrows)
        y += text_height
        self.setRegion(self.s.rows, (-999, y-CH/2, 999999, 999999))
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS

        # set window
        self.size = (XM + maxrows * XS, h + YM + YS * foundrows)


    #
    # Yukon layout
    #  - left: rows
    #  - right: foundations
    #  - left bottom: talon
    #

    def yukonLayout(self, rows, texts=0, playcards=20):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)

        # set size so that at least 2/3 of a card is visible with 20 cards
        h = CH*2/3 + (playcards-1)*self.YOFFSET
        h = YM + max(h, suits*YS)

        # create rows
        x, y = XM, YM
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS
        self.setRegion(self.s.rows, (-999, -999, x - CW / 2, 999999))

        # create foundations
        for suit in range(suits):
            for i in range(decks):
                self.s.foundations.append(S(x+i*XS, y, suit=suit))
            y = y + YS

        # create talon
        x, y = XM, h - YS
        self.s.talon = s = S(x, y)
        if texts:
            # place text right of stack
            self._setText(s, 'se')

        # set window
        self.size = (XM + (rows+decks)*XS,  h)


    #
    # Easy layout
    #  - top: talon, waste, foundations
    #  - bottom: rows
    #

    def easyLayout(self, rows, waste, texts=1, playcards=10, center=1):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        ranks = len(self.game.gameinfo.ranks)
        frows = 4 * decks / (1 + (decks >= 3))
        toprows = 1 + waste + frows
        maxrows = max(rows, toprows)
        yextra = 0

        # set size so that at least 2/3 of a card is visible with 10 cards
        h = CH * 2 / 3 + (playcards - 1) * self.YOFFSET
        h = max(h, 2 * YS)

        # top
        x, y = XM, YM
        self.s.talon = s = S(x, y)
        if texts:
            if waste or not center or maxrows - frows <= 1:
                # place text below stack
                self._setText(s, 's')
                yextra = 20
            else:
                # place text right of stack
                self._setText(s, 'ne')
        if waste:
            x = x + XS
            self.s.waste = s = S(x, y)
            if texts:
                # place text below stack
                self._setText(s, 's')
        x = XM + (maxrows - frows) * XS
        if center and frows + 2 * (1 + waste + 1) <= maxrows:
            # center the foundations
            x = XM + (maxrows - frows) * XS / 2

        x0, y0 = x, y
        for i in range(decks):
            for rank in range(ranks):
                self.s.foundations.append(S(x0, y0, suit=rank))
                x0 = x0 + XS
            if i == 1 and decks > 2:
                x0, y0 = x, y + YS
                y = y0

        # bottom
        x, y = XM, y + YS + yextra * (decks <= 2)
        self.setRegion(self.s.rows, (-999, y - YM / 2, 999999, 999999))
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS

        # set window
        self.size = (XM + maxrows * XS, YM + YS + yextra + h)


    #
    # Samuri layout
    #  - top center: rows
    #  - left & right: foundations
    #  - bottom center: talon
    #

    def samuriLayout(self, rows, waste, texts=1, playcards=20, center=1):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)
        toprows = 2 * decks + rows
        yextra = 0

        # set size so that at least 2/3 of a card is visible with 20 cards
        h = CH * 2 / 3 + (playcards - 1) * self.YOFFSET
        h = max(h, 2 * YS)

        # bottom center
        x = (XM + (toprows * XS) / 2) - XS
        y = h
        self.s.talon = s = S(x, y)
        if texts:
            if waste or not center or toprows - rows <= 1:
                # place text below stack
                self._setText(s, 's')
                yextra = 20
            else:
                # place text right of stack
                self._setText(s, 'ne')
        if waste:
            x = x + XS
            self.s.waste = s = S(x, y)
            if texts:
                # place text below stack
                self._setText(s, 's')

        # left & right
        x, y = XM, YM
        d, x0, y0 = 0, x, y
        for suit in range(12):
            for i in range(decks):
                x0, y0 = x + XS * i, y + YS * d
                self.s.foundations.append(S(x0, y0, suit=suit))
                if i == decks - 1 and suit == 5:
                    x0, y0 = x + XS * (toprows - decks), YM
                    d, x, y = -1, x0, y0
            d = d + 1

        # top center
        x, y = XM + XS * decks, YM
        self.setRegion(self.s.rows, (x - XM / 2, 0, x + XS * rows, 999999))
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS

        # set window
        self.size = (XM + toprows * XS, YM + YS + yextra + h)


    #
    # Sumo layout
    #  - top center: rows
    #  - left & right: foundations
    #  - bottom center: talon
    #

    def sumoLayout(self, rows, reserves, texts=0, playcards=12, center=1):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)
        assert reserves % 2 == 0
        toprows = 12
        maxrows = max(rows, toprows)
        w = XM + maxrows * XS

        # set size so that at least 2/3 of a card is visible with 12 cards
        h = CH * 2 / 3 + (playcards - 1) * self.YOFFSET
        h = max(h, 2 * YS)

        # create foundations
        x, y = XM, YM
        for i in range(decks):
            for suit in range(12):
                self.s.foundations.append(S(x, y, suit=suit))
                x = x + XS
            x, y = XM, y + YS

        # create rows
        x, y = XM + XS * ((toprows - rows) / 2), YM + YS * decks
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS
        self.setRegion(self.s.rows, (XS + XM / 2, YS * decks + YM / 2, XS * 11 - XM / 2, 999999))

        # create reserves
        x, y = XM, YM + YS * decks
        for i in range(reserves / 2):
            self.s.reserves.append(S(x, y))
            y = y + YS
        x, y = w - XS, YM + YS * decks
        for i in range(reserves / 2):
            self.s.reserves.append(S(x, y))
            y = y + YS

        # create talon
        x, y = XM, h + YM
        self.s.talon = s = S(x, y)
        if texts:
            # place text right of stack
            self._setText(s, 'se')

        # set window
        self.size = (XM + toprows * XS, YM + YS + h)


    #
    # Fun layout
    #  - top: rows
    #  - right: foundations
    #  - bottom right: reserves
    #

    def funLayout(self, rows, reserves, texts=0, playcards=12, center=1):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        ranks = len(self.game.gameinfo.ranks)
        assert rows % 2 == 0
        assert reserves % decks == 0
        toprows = decks + rows / 2
        w = XM * 2 + toprows * XS

        # set size so that at least 2/3 of a card is visible with 12 cards
        h = CH * 2 / 3 + (playcards - 1) * self.YOFFSET
        h = max(h, 2 * YS)

        # create foundations
        x, y = w - XS * decks, YM
        for i in range(decks):
            for rank in range(ranks):
                self.s.foundations.append(S(x, y, suit=rank))
                y = y + YS
            x, y = x + XS, YM

        # create rows
        x, y = XM, YM
        for i in range(rows / 2):
            self.s.rows.append(S(x, y))
            x = x + XS
        x, y = XM, (YS + h) / 2
        for i in range(rows / 2):
            self.s.rows.append(S(x, y))
            x = x + XS
        self.setRegion(self.s.rows, (0, 0, XS * rows / 2 + XM / 2, 999999))

        # create reserves
        x, y = w - XS * decks, YM + YS * 4
        for i in range(decks):
            for i in range(reserves / decks):
                self.s.reserves.append(S(x, y))
                y = y + YS
            x, y = x + XS, YM + YS * 4

        # create talon
        x, y = XM, h
        self.s.talon = s = S(x, y)
        if texts:
            # place text right of stack
            self._setText(s, 'se')

        # set window
        self.size = (w, YM + YS + h)


    #
    # Oonsoo layout
    #  - top: talon & rows
    #  - left: reserves
    #  - center right: rows
    #

    def oonsooLayout(self, rows, reserves, texts=0, playcards=12, center=1):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        assert rows % 2 == 0
        toprows = decks + rows / 2
        w = XM * 2 + toprows * (XS + XM)

        # set size so that at least 2/3 of a card is visible with 12 cards
        h = CH * 2 / 3 + (playcards - 1) * self.YOFFSET
        h = max(h, 2 * YS)

        # create talon
        x, y = XM, YM
        self.s.talon = s = S(x, y)
        if texts:
            # place text below stack
            self._setText(s, 's')

        # create rows
        x, y = XS + XM * 3, YM
        for i in range(rows / 2):
            self.s.rows.append(S(x, y))
            x = x + XS + XM
        x, y = XS + XM * 3, (YS + h) / 2
        for i in range(rows / 2):
            self.s.rows.append(S(x, y))
            x = x + XS + XM
        self.setRegion(self.s.rows, (XS + XM, -999, 999999, 999999))

        # create reserves
        x, y = XM, YM + YS + self.TEXT_HEIGHT
        for i in range(decks):
            for i in range(reserves / decks):
                self.s.reserves.append(S(x, y))
                y = y + YS
            x, y = x + XS, YM + YS * 4

        # set window
        self.size = (w, YM + YS + h)


    #
    # Ghulam layout
    #  - left & right: foundations & reserves
    #  - center: two groups of rows
    #  - lower right: talon
    #

    def ghulamLayout(self, rows, reserves=0, texts=0):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits)
        assert rows % 2 == 0
        assert reserves % 2 == 0

        # set size
        w, h = XM * 3 + XS * ((rows / 2) + 2), YM + YS * ((suits / 2) + 2)

        # create foundations
        x, y = XM, YM
        for i in range(suits):
            self.s.foundations.append(S(x, y, suit=i))
            y = y + YS
            if i == suits / 2 - 1:
                x, y = w - XS, YM

        # create rows
        x = XM * 2 + XS
        for i in range(rows / 2):
            self.s.rows.append(S(x + i * XS, YM))
        for i in range(rows / 2):
            self.s.rows.append(S(x + i * XS, h / 2))
        self.setRegion(self.s.rows, (XM + XS, -999, w - XM - XS, 999999))

        # create reserves
        for i in range(reserves / 2):
            self.s.reserves.append(S(XM, h - YS * (i + 1)))
        for i in range(reserves / 2):
            self.s.reserves.append(S(w - XS, h - YS * (i + 1)))

        # create talon
        self.s.talon = s = S(w - XS * 2, h - YS)
        if texts:
            assert 0

        # set window
        self.size = (w, h)


    #
    # Generiklon layout
    #  - top: talon & foundations
    #  - bottom: rows
    #

    def generiklonLayout(self, rows, waste = 1, height = 6):
        S = self.__createStack
        CW, CH = self.CW, self.CH
        XM, YM = self.XM, self.YM
        XS, YS = self.XS, self.YS

        decks = self.game.gameinfo.decks
        suits = len(self.game.gameinfo.suits) + bool(self.game.gameinfo.trumps)
        frows = suits * decks / 2
        fspace = XS * (rows - 1) / 2

        # Set window size
        w, h = XM + XS * rows, YM * 2 + YS * height
        self.size = (w, h)

        # Talon
        x, y = XM, YM
        self.s.talon = s = S(x, y)
        self._setText(s, 'se')
        self.s.waste = s = S(x, y + YS)
        self._setText(s, 'se')

        # Create foundations
        x = w - fspace - XS * frows / 2
        for suit in range(suits / 2):
            for i in range(decks):
                self.s.foundations.append(S(x, y, suit = suit))
                x = x + XS
        x = w - fspace - XS * frows / 2
        y = y + YS
        for suit in range(suits / 2):
            for i in range(decks):
                self.s.foundations.append(S(x, y, suit = suit + suits / 2))
                x = x + XS

        # bottom
        x, y = XM, YM * 2 + YS * 2
        for i in range(rows):
            self.s.rows.append(S(x, y))
            x = x + XS
        self.setRegion(self.s.rows, (-999, y - YM, 999999, 999999))

