class MasterModel(object):
    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site


class MasterSite(object):
    def __init__(self):
        self._registry = {}

    def register(self,model_class,master_class=None):
        if not master_class:
            master_class = MasterModel
        self._registry[model_class] = master_class(model_class,self)
site = MasterSite()