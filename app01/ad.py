from webmaster.server import sites
from app01 import models


class MyMasterModel(sites.MasterModel):
    list_display = ["id","username","password","email"]
sites.site.register(models.UserInfo, MyMasterModel)
sites.site.register(models.UserType)