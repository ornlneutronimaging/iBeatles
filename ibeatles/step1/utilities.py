def get_tab_selected(parent=None):
    '''
    return: 'sample', 'ob' or 'normalized'
    
    '''
    main_tab_index = parent.ui.tabWidget.currentIndex()
    if main_tab_index == 2:
        return 'normalized'
    else:
        load_data_index = parent.ui.toolBox.currentIndex()
        if load_data_index == 0:
            return 'sample'
        if load_data_index == 1:
            return 'ob'
    return -1
