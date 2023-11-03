from .models import SearchWriteSql

# 下次搜索不需要requests_save
def judgmentdata(host,link):
    # 判断是否已经存在
    entry_to_modify = SearchWriteSql.objects.filter(host=host,link=link).first()
    if entry_to_modify:
        entry_to_modify.is_valid = False
        entry_to_modify.save()
        return True
    else:
        return False

