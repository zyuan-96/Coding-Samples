#!/usr/bin/env python3

from transformation import *
from plotting import *
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

'''
Creates an interactive plotting GUI
'''

class AppStack(QtWidgets.QWidget):

    def __init__(self):
        '''
        Initializes application stack, consisting of a stack object and an
         object representing the list of elements on the stack.
        '''
        self.qapp = QtWidgets.QApplication(sys.argv)
        super().__init__()
        stack = QtWidgets.QStackedWidget(self)
        stacklist = self.build_stacklist()
        self.stacklist_index = 0 # initialized to list beginning
 
        self.stacklist = self.resize_widget(stacklist, [0,0,1,0.05])
        self.stack = self.resize_widget(stack, [0,0.05,1,0.95])

    def build_stacklist(self):
        '''
        Builds the object representing the list of elements on the stack.

        No Inputs.

        Returns QListWidget, list of elements on the stack.
        '''
        stacklist = QtWidgets.QListWidget(self)
        stacklist.setFlow(QtWidgets.QListWidget.LeftToRight)
        stacklist.currentRowChanged.connect(self.display_page)
        return stacklist

    def display_page(self, index):
        '''
        Event handler for switching between pages on the stack.
        
        Inputs:
         index (integer): represents which page is currently displayed.
        '''
        self.stack.setCurrentIndex(index)

    def add_to_stack(self, page, name):
        '''
        Adds page to stack and stack list objects, incrementing the index for
         the next object to be placed on the stack.

        Inputs:
         page (QWidget): a page to add to the stack,
         name (string): a unique indicator for the corresponding page.
        '''
        self.stack.addWidget(page)
        SPACING = '    '
        stack_label = SPACING + name + SPACING
        self.stacklist.insertItem(self.stacklist_index, stack_label)
        self.stacklist_index += 1

    def get_screen_resolution(self):
        '''
        Gets the current display screen resolution, in pixels.

        No Inputs.

        Returns list of width and height resolution dimensions, in pixels.
        '''

        desktop = QtWidgets.QDesktopWidget()
        width = desktop.screenGeometry().width()
        height = desktop.screenGeometry().height()
        return [width, height]

    def resize_widget(self, widget, dimensions):
        '''
        Sets the geometry of a widget, by ratio of the window screen
         dimensions (e.g., width = 0.8 -> 80% of the screen width).

        Inputs:
         widget (QtWidget object): pyqt widget to be resized,
         dimensions (list): dimensions for widget to be resized to, each in
                            terms of a ratio of the corresponding window
                            dimension.

        Returns resized widget.
        '''
        screen_width, screen_height = self.get_screen_resolution()
        x_ratio, y_ratio, width_ratio, height_ratio = dimensions

        x_position = x_ratio*screen_width
        y_position = y_ratio*screen_height
        width = width_ratio*screen_width
        height = height_ratio*screen_height

        widget.setGeometry(QtCore.QRect(x_position, y_position, width, height))
        return widget



class App(QtWidgets.QWidget):

    def __init__(self, alone=True):
        '''
        Initializes a QApplication object instance.

        Returns an App class instance.
        '''
        # Passes in sys.argv to allow acces to command line arguments passed to
        #  the script. Initializes the __init__ method of the parent class, to
        #  allow access to builtin functions (e.g., setWindowTitle, 
        #  setGeometry, etc.).
        if alone:
            self.qapp = QtWidgets.QApplication(sys.argv)
        super().__init__()

        # Open hidden PyQt window.
        #self.showMaximized()

    def get_screen_resolution(self):
        '''
        Gets the current display screen resolution, in pixels.

        No Inputs.

        Returns list of width and height resolution dimensions, in pixels.
        '''

        desktop = QtWidgets.QDesktopWidget()
        width = desktop.screenGeometry().width()
        height = desktop.screenGeometry().height()
        return [width, height]

    def resize_widget(self, widget, dimensions):
        '''
        Sets the geometry of a widget, by ratio of the window screen
         dimensions (e.g., width = 0.8 -> 80% of the screen width).

        Inputs:
         widget (QtWidget object): pyqt widget to be resized,
         dimensions (list): dimensions for widget to be resized to, each in
                            terms of a ratio of the corresponding window
                            dimension.

        Returns resized widget.
        '''
        screen_width, screen_height = self.get_screen_resolution()
        x_ratio, y_ratio, width_ratio, height_ratio = dimensions

        x_position = x_ratio*screen_width
        y_position = y_ratio*screen_height
        width = width_ratio*screen_width
        height = height_ratio*screen_height

        widget.setGeometry(QtCore.QRect(x_position, y_position, width, height))
        return widget

    def embed_figure(self, figure, dimensions):
        '''
        Embeds a seaborn figure into GUI window.
    
        Inputs:
         figure (seaborn figure): seaborn figure object to be embedded,
         dimensions (list): dimensions for widget to be resized to, each in
                            terms of a ratio of the corresponding window
                            dimension.

        Returns canvas object, for later updating.
        '''

        # Gets a QtWidget frame and a QtWidget container
        widget = QtWidgets.QWidget(self)
        frame = self.resize_widget(widget, dimensions)
        canvas_container = QtWidgets.QVBoxLayout()
    
        # Converts figure to canvas and frames resulting canvas
        canvas = Canvas(figure)
        canvas_container.addWidget(canvas)
        frame.setLayout(canvas_container)

        return canvas

    def update_figure(self, selector, canvas, visual):
        '''
        Updates the data in an embedded seaborn figure.

        Inputs:
         canvas (FigureCanvas instance): seaborn figure converted to a canvas,
         keyword (string): represents which keyword to get frequency data from.
        '''

        axes = canvas.figure.axes
        selected = [item.text() for item in selector.selectedItems()]
        keywords = selected if selected else ''
        update_plot(visual, keywords, axes, canvas)

    def embed_data_selector(self, selections, dimensions, canvas, visual,
                            multiselect=False):
        '''
        Embeds a data selection list.

        Inputs:
         selections (list): contents to select from,
         dimensions (list): dimensions for widget to be resized to, each in
                            terms of a ratio of the corresponding window
                            dimension,
         multiselect (boolean): determines whether multiple selections can be
                                selected at the same time.

        Returns a selector object.
        '''

        # Creates a selector widget.
        ROW_LENGTH = 1
        column_length = len(selections)
        selector = QtWidgets.QTableWidget(column_length, ROW_LENGTH, self)

        # Sets items of selector table.
        ROW = 0
        for column, selection in enumerate(selections):
            item = QtWidgets.QTableWidgetItem(str(selection))
            selector.setItem(ROW, column, item)

        # Blocks editing of selections.
        selector.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Conditionally turns on multiselection feature.
        if multiselect:
            selection_mode = QtWidgets.QAbstractItemView.ExtendedSelection
        else:
            selection_mode = QtWidgets.QAbstractItemView.SingleSelection
        selector.setSelectionMode(selection_mode)

        # Sets size adjust policy, so column width will be filled to show all 
        # of the available text.
        size_adjust_policy = QtWidgets.QAbstractScrollArea.AdjustToContents
        selector.setSizeAdjustPolicy(size_adjust_policy)
        selector.resizeColumnsToContents()

        # Sets function for updating on a changed selection.
        partial = lambda function, *arguments: lambda: function(*arguments)
        selector.itemSelectionChanged.connect(partial(self.update_figure,
                                                      selector, canvas,
                                                      visual))
        selector = self.resize_widget(selector, dimensions)

        return selector

if __name__ == "__main__":
    app_stack = AppStack()
    visuals = {0: 'Media v. Twitter Frequency Comparison',
               1: 'Cumulative Twitter Frequency',
               2: 'Keyword Matching'}

    SEED_APPLICATION = False

    main_app = App(SEED_APPLICATION)
    figure, axes = plot_seed(visuals[0])
    canvas = main_app.embed_figure(figure, [0, 0, 0.8, 0.85])
    keywords = cumulative_news_words
    main_app.embed_data_selector(keywords, [0.8, 0, 0.2, 0.85],
                                 canvas, visuals[0])
    app_stack.add_to_stack(main_app, 'Frequency Correlation')

    main_app = App(SEED_APPLICATION)
    figure, axes = plot_seed(visuals[1])
    canvas = main_app.embed_figure(figure, [0,0,0.8,0.9])
    app_stack.add_to_stack(main_app, 'Cumulative Frequency')
    keywords = cumulative_tweets_words
    main_app.embed_data_selector(keywords, [0.8, 0, 0.2, 0.9],
                                 canvas, visuals[1], True)

    main_app = App(SEED_APPLICATION)
    figure, axes = plot_seed(visuals[2])
    canvas = main_app.embed_figure(figure, [0,0,0.8,0.9])
    main_app.embed_data_selector(news_sources, [0.8, 0, 0.2, 0.9],
                                 canvas, visuals[2], True)
    app_stack.add_to_stack(main_app, 'Matches')

    app_stack.showMaximized()
    sys.exit(app_stack.qapp.exec_())
