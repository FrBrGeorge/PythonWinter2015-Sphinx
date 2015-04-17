#!/usr/bin/env python
# coding: utf
'''
Simple input box for pygame

Usage:

.. code-block:: python    

    box=Input(…)                                    # declare an input box
    while <main loop>:
        …
        if box.is_active() and <event goes to box>: # currently in input state
            box.edit(event)                         # pass event to the box
        else:
            <parse eventsd normally>
        …
        if box.is_done():                           # input is finished …
            if box.is_cancelled():                  # …with cancel
                <"no input is needed" action>
            elif box.is_failed():                   # …unsuccessfully
                <unsuccessfull input action>
            else:                                   # …succsessfuly
                <succsessful input action>
            box.deactivate()                        # hide box and resore state
        …
        if <input is needed>:                       # we need to input something in program
            box.activate(…)                         # store old state and turn on the box
        …
        if box.is_active():
            box.draw(surface,pos)                   # show box after all surface changes
        pygame.display.flip()                       # display the picture
        if box.is_active():
            box.undraw()                            # hide box before further surface changes
'''

import pygame
__VERSION__=0.06

ACTIVE,DONE,FAILED,CANCEL,SHOWN,FIRST=(1<<i for i in xrange(6))

class Input:
    '''
    Interactive text box providing typed input
    '''
    # Default values for some properties
    BorderWidth=3
    Status=0
    CursorWidth=2
    Margin=0
    TextColor=pygame.Color("Black")
    PromptColor=pygame.Color("grey50")
    CursorColor=pygame.Color("grey75")
    OverColor=pygame.Color("tomato")
    PaperColor=pygame.Color("ivory")
    Prompt=u""
    DefaultText=u""
    SetType=unicode
    RetryIncorrect=True
    TextLength=8
    FontID=None
    Font=None
    FontSize=24
    PromptGap=None
    Size=None
    FixedSize=False
    BackingStore=None
    RepeatStore=None
    RepeatDefault=(500,100)

    def __update__(self, *pargs, **nargs):
        '''Update box properties.
        Positional parameters: [Prompt, [DefaultText]].
        Named parameters: all class data fields.

        - Size supercedes FontSize, default FontSize is 24
        - setting DefaultText also sets SetType (so use 0., not "0" for float input)
        '''
        if len(pargs)>0:
            self.Prompt=pargs[0]
        if len(pargs)>1:
            self.DefaultText=unicode(pargs[1])
            self.SetType=type(pargs[1])
        for prop in nargs:
            if hasattr(self,prop):
                setattr(self,prop,nargs[prop])
        if not self.FontID:
            self.FontID=pygame.font.match_font("sans")
        if self.PromptGap is None and self.Prompt:
            self.PromptGap=" "
        if "SetType" not in nargs and "DefaultText" in nargs:
            self.SetType=type(nargs["DefaultText"])
        if "TextLength" not in nargs and self.DefaultText:
            self.TextLength=0
        if "Size" in nargs:
            self.FixedSize=True
            self.FontSize=self.Size[1]-2*self.BorderWidth
            self.Font=pygame.font.Font(self.FontID, self.FontSize)
        elif not self.Size or not self.FixedSize:
            self.Font=pygame.font.Font(self.FontID, self.FontSize)
            self.Size=self.Font.size(self.Prompt+self.PromptGap+"W"*max(self.TextLength,len(self.DefaultText)+1,2))
            self.Size=self.Size[0]+2*self.BorderWidth,self.Size[1]+2*self.BorderWidth
        self.Paper=pygame.Surface(self.Size)
        # TODO background image/transparency for Paper
        self.Paper.fill(self.PaperColor)
        pr=self.Font.render(self.Prompt, True, self.PromptColor)
        self.Paper.blit(pr, (self.BorderWidth,(self.Size[1]-pr.get_height())/2))
        self.Text=unicode(self.DefaultText)
        self.Cursor=len(self.Text)

    def __init__(self, *pargs, **nargs):
        '''Create a text input entity. Call __update__() next.'''
        self.__update__(*pargs, **nargs)

    def __sawtoothed__(self, block, side, mult=3):
        '''Create a sawtoothed mark for left (False) or right (True) side

        :param rect block: Rectangle to scale sawtooth on
        :param bool side: Choose left (``False``) or right (``True``) side
        :param int mult: Tooth scale

        :return: List of coordinates for :py:func:`pygame.draw.polygon()`
        '''
        w,h=block.get_size()
        nw=mult*self.BorderWidth
        n=(h/nw)|1
        x,d=side and (w-1,-nw) or (0,nw)
        return [(x+d*(i%2),h*i/n) for i in xrange(n)]

    def value(self):
        '''Check if input is correct and return it, return None if it is not'''
        try:
            return self.SetType(self.Text)
        except:
            try:
                return self.SetType(str(self.Text))
            except:
                return None

    def render(self):
        '''Return paper surface with current prompt and text printed on'''
        ret=self.Paper.copy()
        wl=self.Font.size(self.Prompt+self.PromptGap)[0]
        ib=ret.subsurface((wl,0,ret.get_width()-wl,ret.get_height()))
        ia=ret.subsurface((wl+self.BorderWidth,self.BorderWidth,ret.get_width()-wl-2*self.BorderWidth,ret.get_height()-2*self.BorderWidth))
        pr=self.Font.render(self.Text, True, self.TextColor)
        w=self.Font.size(self.Text[:self.Cursor])[0]
        while self.Margin and w-self.Font.size(self.Text[:self.Margin])[0]<self.CursorWidth and self.Margin>0:
            self.Margin-=1
        while w-self.Font.size(self.Text[:self.Margin])[0]>ia.get_width()-self.CursorWidth and self.Margin<len(self.Text):
            self.Margin+=1
        Offset=-self.Font.size(self.Text[:self.Margin])[0]
        ia.blit(pr,(Offset,(ia.get_height()-pr.get_height())/2))
        pygame.draw.line(ia, self.CursorColor, (w+Offset,2), (w+Offset,ia.get_height()-2),self.CursorWidth)
        if Offset<0:
            pygame.draw.polygon(ib, self.OverColor, self.__sawtoothed__(ib, False))
        if Offset+pr.get_width()>ia.get_width()-self.CursorWidth:
            pygame.draw.polygon(ib, self.OverColor, self.__sawtoothed__(ib, True))
        return ret

    def draw(self,scr,pos):
        '''Draw input box on surface scr at position pos
        backuping an underlying part of surface'''
        self.BackingStore=(self.Paper.copy(),scr,pos)
        self.BackingStore[0].blit(self.BackingStore[1],(0,0),(self.BackingStore[2],self.Size))
        self.BackingStore[1].blit(self.render(),self.BackingStore[2])
        self.Status|=SHOWN

    def undraw(self):
        '''Remove the box from the surface it was drawn
        restoring underlying part of surface'''
        if self.BackingStore:
            self.BackingStore[1].blit(self.BackingStore[0],self.BackingStore[2])
        self.Status&=~SHOWN

    def activate(self, *pargs, **nargs):
        '''Enable input from the box.

        If either pargs or nargs is given, call :py:meth:`.__update__`.

        :return: ``False`` if no activation was needed, ``True`` otherwise.

        Calling :py:meth:`.__update__` means resetting every field,
        so use `inputbox.activate("*any prompt*")' to replace
        last entered value with the default one.
        '''
        if self.Status&ACTIVE and not pargs and not nargs:
            return False
        if pargs or nargs:
            self.__update__(*pargs, **nargs)
        self.Cursor=len(self.Text)
        self.Margin=0
        self.Status=ACTIVE|FIRST
        self.RepeatStore=pygame.key.get_repeat()
        pygame.key.set_repeat(*self.RepeatDefault)
        return True

    def deactivate(self):
        '''Disable input from the box'''
        if self.Status:
            self.Status=0
            pygame.key.set_repeat(*self.RepeatStore)

    def is_active(self): return self.Status&ACTIVE
    def is_done(self): return self.Status&DONE
    def is_failed(self): return self.Status&FAILED
    def is_cancelled(self): return self.Status&CANCEL
    def is_shown(self): return self.Status&SHOWN

    def is_success(self):
        return self.is_done() and not (self.is_failed() or self.is_cancelled())

    def edit(self,ev):
        '''
        Proceed event for editing input box.

        :param event ev: Event to parse

        Supported keys:

        * ``any unicode symbol``:   input character
        * ``Return``/``Enter``:     finish input
        * ``Backspace``/``Del``:    delete character under/after the cursor
        * ``Esc``:                  restore default value
        * ``Home``/``End``/→/←:     move cursor
        * ``Esc`` ``Esc``:          cancel input
        '''
        if ev.type is pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                if self.Cursor>0:
                    self.Text=self.Text[:self.Cursor-1]+self.Text[self.Cursor:]
                    self.Cursor-=1
            elif ev.key == pygame.K_DELETE:
                if self.Cursor<len(self.Text):
                    self.Text=self.Text[:self.Cursor]+self.Text[self.Cursor+1:]
            elif ev.unicode >= u' ':
                if self.Status&FIRST:
                    self.Text=ev.unicode
                    self.Cursor=1
                else:
                    self.Text=self.Text[:self.Cursor]+ev.unicode+self.Text[self.Cursor:]
                    self.Cursor+=1
            elif ev.key == pygame.K_ESCAPE:
                if self.Text==self.DefaultText:
                     self.Status|=CANCEL|DONE
                self.Text=self.DefaultText
                self.Margin=0
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.value() is None:
                    if self.RetryIncorrect:
                        # TODO signal an error
                        self.Text=self.DefaultText
                        self.Margin=0
                    else:
                        self.Status|=DONE|FAILED
                else:
                    self.Status|=DONE
            elif ev.key == pygame.K_HOME:
                self.Cursor=0
            elif ev.key == pygame.K_END:
                self.Cursor=len(self.Text)
            elif ev.key == pygame.K_RIGHT:
                self.Cursor=min(self.Cursor+1,len(self.Text))
            elif ev.key == pygame.K_LEFT:
                self.Cursor=max(self.Cursor-1,0)
            self.Status&=~FIRST

    def input(self, scr, pos, *pargs, **nargs):
        '''
        Perform synchronous input on surface scr at position pos.

        :param surface scr: Surface to draw textbox
        :param int,int pos: Top-left coordinates of textbox

        All additional parameters are passed to :py:meth:`.activate` method.

        All unused events are ignored.'''
        self.activate(*pargs, **nargs)
        while not self.is_done():
            self.edit(pygame.event.wait())
            self.draw(scr,pos)
            pygame.display.flip()
            self.undraw()
        self.deactivate()
        return self.value()

def Print(scr, text, pos=None, font=None, size=24, antialias=True, color=None, background=None):
    ''' 
    Print text on surface using as many defaults as possible

    :param surface scr: Surface to print the string
    :param str text: String to print
    :param int,int pos: Top-left corner of output box (default is centered by src)
    :param font font: Font to render
    :param int size: Font size (default is 24)
    :param bool antialias: Where to use antialiasing or not
    :param color color: Text color (use background-contrast by default)
    :param color background: Background color (transparent by default)
    '''
    # TODO font is registered every time you print, fix this
    f=pygame.font.Font(font, size)
    if pos == None:
        pos=scr.get_size()
        sz=f.size(text)
        pos=(pos[0]-sz[0])/2,(pos[1]-sz[1])/2
    if color == None:
        color=scr.get_at(pos)
        color.r, color.g, color.b = 255^color.r, 255^color.g, 255^color.b
    if background:
        pr=f.render(text, antialias, color, background=background)
    else:
        pr=f.render(text, antialias, color)
    scr.blit(pr, pos)

def __main():
    import random
    _=random.randint
    pygame.init()
    Size=(760,180)
    Scr=pygame.display.set_mode(Size)
    Scr.fill(pygame.Color("Black"))
    r=20
    x,y=Size[0]/12,Size[1]/5
    inp=Input("Input",Size=(Size[0]-2*x,Size[1]-2*y))
    cont,verbose=True,False
    defaults,defcnt=(("String",u""),("Int",0),("Float",0.)),0
    print "Press ENTER to input, F1 to toggle verbosity, ESC to exit"
    while cont:
        pos=_(r,Size[0]-r),_(r,Size[1]-r)
        col=_(10,255),_(10,255),_(10,255)
        pygame.draw.circle(Scr,col,pos,r)
        for ev in pygame.event.get():
            if verbose:
                print ev
            if ev.type is pygame.QUIT:
                cont=False
            if ev.type is pygame.KEYDOWN and inp.is_active():
                inp.edit(ev)
            elif ev.type is pygame.KEYDOWN:
                if ev.key in (pygame.K_KP_ENTER, pygame.K_RETURN, 13):
                    if not inp.is_active():
                        inp.activate(*defaults[defcnt])
                        print "Input:",defaults[defcnt][0]
                        defcnt=(defcnt+1)%len(defaults)
                elif ev.key == pygame.K_F1:
                    verbose=True
                elif ev.key is pygame.K_ESCAPE:
                    if not inp.is_active():
                        cont=False

        if inp.is_done():
            if inp.is_failed():
                print "Data incorrect"
            elif inp.is_cancelled():
                print "Input is cancelled"
            else:
                print u"Result: '{0}'".format(inp.value())
            inp.deactivate()

        if inp.is_active(): inp.draw(Scr,(x,y))
        pygame.display.flip()
        if inp.is_active(): inp.undraw()
    quit()

if __name__ == "__main__":
    __main()
