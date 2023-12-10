from django.db import models

# host,link列表 
class SearchWriteSql(models.Model):
    host = models.CharField(max_length=200)
    link = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    # 收否有效,需要研判，如果无效则不再requests_save
    is_valid = models.BooleanField(default=True)
    # 是否被研判过
    is_judgment = models.BooleanField(default=False)

# 每次保存到es的uuid
class SearchWriteEs(models.Model):
    esuuid = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    link = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

# 任务列表
class SearchList(models.Model):
    uuid = models.CharField(max_length=200)
    target_url = models.TextField()
    request_body = models.TextField(null=True,default='{}')
    target_name = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
