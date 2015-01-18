# ----------------------------------------------------------------------------
# Tox
# Copyright (c) 2015 Jatniel Prinsloo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
"""
    Tox - Tkinter wrapper with context support --- with context

    [This is how it's used]

    from tox import *
    with Tk():
        with Frame():
            label = Label('Nothing to see here')
            @Button('Hello world')
            def do_hello_world():
                label['text']='Hello you'
"""

import Tkinter,contextlib
from collections import defaultdict

contexts = list()
def _cast(cls):
    def create(*a,**k):
        if contexts:
            container,content = contexts[-1]
            new = cls(container,*a,**k)
            content.append(new)
            return new
        return cls(None,*a,**k)
    create.__doc__ = cls.__doc__
    return create


def _container(cls):
    @contextlib.contextmanager
    def create(side=0,fill=0,**k):
##        master, master_contents =None,None
##        if contexts:
##            master,master_contents = contexts[-1]
##        new = cls(master,)
##        if master_contents is not None:
##            master_contents.append(new)

        contents = []
        contexts.append((new,contents))
        yield new
        #print cls,contents
        for element in contents:
            #print cls,new,element

            element.pack(
                side = (Tkinter.TOP,Tkinter.LEFT,Tkinter.BOTTOM,Tkinter.RIGHT)[side],
                fill = (Tkinter.NONE,Tkinter.X,Tkinter.Y,Tkinter.BOTH)[fill],
                expand = True,
                **k
                )
        contexts.pop()

    create.__doc__ = cls.__doc__
    #create.__init__ = cls.__init__

    return create
class ToxMeta(type):
    #@classmethod
    def __lshift__(cls,other):
        return type(other.__name__,(cls,other),{'_wrapclass':other})
class ToxContent(object):
    __metaclass__=ToxMeta
    _wrapclass = None
##    def __new__(cls,*a,**k):
##        if len(a)==1 and not k and issubclass(a[0],Tkinter.BaseWidget):
##            return
##        else:
##            return object.__new__(cls,*a,**k)
    def __init__(self,**k):
        wrapclass = self._wrapclass

        master, contents = None,None
        if contexts:
            master,contents = contexts[-1]

        wrapclass.__init__(self,master,**k)

        if contents is not None:
            contents.append(self)

class ToxContainer(ToxContent):
    def __init__(self,side=0,fill=0,expand=True,**k):
        ToxContent.__init__(self,**k)
        self.contents = []

        self.side = side
        self.fill = fill
        self.expand = expand
        self.kwds = k
    def __enter__(self):
        contexts.append((self,self.contents))
        return self
    def __exit__(self,*a):

        for element in self.contents:
            #print cls,new,element
            print element
            element.pack(
                side = (Tkinter.TOP,Tkinter.LEFT,Tkinter.BOTTOM,Tkinter.RIGHT)[self.side],
                fill = (Tkinter.NONE,Tkinter.X,Tkinter.Y,Tkinter.BOTH)[self.fill],
                expand = self.expand,
                **self.kwds
                )
        contexts.pop()
        self.contents=[]
        return True


class Tk(ToxContainer<<Tkinter.Tk):
    def __init__(self,mainloop=True,*a,**k):
        self.auto_mainloop=mainloop
        ToxContainer.__init__(self,*a,**k)
    def __exit__(self,*a):
        result = ToxContainer.__exit__(self,*a)
        if self.auto_mainloop:
            self.mainloop()
        return result
class Frame(ToxContainer<<Tkinter.Frame):
    pass



#Frame   = _container(Tkinter.Frame)
#Tk      = _container(Tkinter.Tk)
Grid    = _container(Tkinter.Grid)

class Button(ToxContent<<Tkinter.Button):
    def __init__(self,text='',*a,**k):
        self.callbacks = []
        ToxContent.__init__(self,text=text,command=self.callback,*a,**k)
    def callback(self):
        for call in self.callbacks:
            call()

    def __call__(self,func):
        self.callbacks.append(func)
    def bind(self,event_id,func=None,add=True):
        if not func:
            def assign(func):
                return self.bind(event_id,func,add)
            return assign
        else:
            return Button.bind(self,event_id,func,add)


class Label(ToxContent<<Tkinter.Label):
    def __init__(self,text='',*a,**k):
        ToxContent.__init__(self,text=text)

#Label   = _cast(Tkinter.Label)
Listbox = _cast(Tkinter.Listbox)
Canvas  = _cast(Tkinter.Canvas)
Entry   = _cast(Tkinter.Entry)
def example_calculator():
    import operator
    class constants:
        stack = []
        last_op = None
        viewing = False
    with Tk() as root:
        with Frame(0,3):
            entry = Entry()
            with Frame(1,3):
                with Frame(0,3):
                    def button_press(num):
                        def do():

                            if constants.viewing:
                                constants.viewing=False
                                stream = entry.get()
                                entry.delete(0,len(stream))
                            entry.insert(Tkinter.END,str(num))
                        return do

                    with Frame(1,3):
                        Button(text='1')(button_press(1))
                        Button(text='2')(button_press(2))
                        Button(text='3')(button_press(3))
                    with Frame(1,3):
                        Button(text='4')(button_press(4))
                        Button(text='5')(button_press(5))
                        Button(text='6')(button_press(6))
                    with Frame(1,3):
                        Button(text='7')(button_press(7))
                        Button(text='8')(button_press(8))
                        Button(text='9')(button_press(9))
                    with Frame(1,3):
                        Button(text='0')(button_press(0))
                with Frame(0,3):
                    def button_calculate(op):
                        def do():
                            stream = entry.get()
                            value = int(stream)
                            constants.stack.append(value)
                            constants.viewing = True
                            if len(constants.stack)==2:
                                entry.delete(0,len(stream))
                                value = op(*constants.stack)
                                entry.insert(0,str(value))
                                constants.stack = [value]
                        return do

                    Button('+')(button_calculate(operator.add))
                    Button('-')(button_calculate(operator.sub))
                    Button('/')(button_calculate(operator.div))
                    Button('*')(button_calculate(operator.mul))
                    Button('=')(button_calculate(operator.add))

def example_hello_world():
    import random
    with Tk() as root:
        with Frame():
            label = Label(text='--Nothing to see here--')
            @Button('Hello world')
            def do_hello_world():
                label['text']=random.choice(['Hello you','Hi','World Hello','Hey','How are you','Good Day'])

if __name__=='__main__':
    with Tk() as root:
        with Frame(fill=3):
            Label("Tox demo's")
            with Frame(fill=3):
                Button('Hello World')(example_hello_world)
                Button('Calculator')(example_calculator)




