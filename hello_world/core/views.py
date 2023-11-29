from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json
from .search import TimingSearch,TimingSearchStop,SearchEsdata,NotifyRobot_file
from .judgment import judgmentdata
import sys

def index(request):
    return render(
        request,
        "index.html",
        {
            "title": "Django example",
        },
    )

# 启动搜索API
@csrf_exempt
def RunSearchApi(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        uuid,query = TimingSearch(params)
        from .models import SearchList
        new_entry = SearchList(uuid=uuid,query=query,minutes=params['minutes'])
        new_entry.save()
        return JsonResponse({'status': 'success', 'uuid': uuid})
    else:
        # print("开始消息发送")
        # NotifyRobot_file("中融汇信期货有限公司")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# 停止搜索API
@csrf_exempt
def StopSearchApi(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        uuid = params['uuid']
        from .models import SearchList
        entry_to_modify = SearchList.objects.filter(uuid=uuid).first()
        if entry_to_modify:
            entry_to_modify.delete()
        if TimingSearchStop(uuid):
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'stop error'})
    else:
        print("终止服务")
        sys.exit()
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# 下一次搜索不需要requests_save
@csrf_exempt
def JudgmentApi(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        link = params['link']
        host = params['host']
        if judgmentdata(host,link):
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'stop error'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# 获取全部未研判的数据
@csrf_exempt
def GetJudgmentDataApi(request):
    if request.method == 'POST':
        from .models import SearchWriteSql
        entry_to_modify = SearchWriteSql.objects.filter(is_judgment=True)
        if entry_to_modify:
            return JsonResponse({'status': 'success','data':entry_to_modify})
        else:
            return JsonResponse({'status': 'error', 'data': 'no data'})

# 获取某条需要研判的数据es的uuid
@csrf_exempt
def GetJudgmentEsUuidApi(request):
    if request.method == 'POST':
        from .models import SearchWriteEs
        params = json.loads(request.body)
        link = params['link']
        host = params['host']
        entry_to_modify = SearchWriteEs.objects.filter(host=host,link=link).first()
        if entry_to_modify:
            return JsonResponse({'status': 'success','data':entry_to_modify.esuuid})
        else:
            return JsonResponse({'status': 'error', 'data': 'no data'})

# 基于es的uuid查询数据
@csrf_exempt
def EsDataApi(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        uuid = params['uuid']
        esdata = SearchEsdata(uuid)
        if esdata:
            return JsonResponse({'status': 'success','data':esdata})
        else:
            return JsonResponse({'status': 'error', 'data': 'no data'})

# 获取搜索任务列表
@csrf_exempt
def GetSearchListApi(request):
    if request.method == 'POST':
        from .models import SearchList
        entry_to_modify = SearchList.objects.all()
        if entry_to_modify:
            data = serializers.serialize('json', entry_to_modify)
            return JsonResponse({'status': 'success','data':data},safe=False)
        else:
            return JsonResponse({'status': 'error', 'data': 'no data'})