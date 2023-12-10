from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json
from .search import TimingSearch,TimingSearchStop,SearchEsdata,NotifyRobot_file
from .judgment import judgmentdata
import sys
import uuid

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
        random_uuid = str(uuid.uuid4())
        params['random_uuid'] = random_uuid
        TimingSearch(params)
        from .models import SearchList
        new_entry = SearchList(uuid=random_uuid,target_url=params['target_url'],target_name=params['name'],request_body=str(request.body))
        new_entry.save()
        return JsonResponse({'status': 'success', 'uuid': random_uuid})
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
            return JsonResponse({'status': 'failed', 'message': 'Has stop'})
    else:
        # print("终止服务")
        # sys.exit()
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
        entry_to_modify = SearchList.objects.all().order_by('-pub_date')
        if entry_to_modify:
            # 创建每个条目的字典，并添加到数据列表中
            data = [
                {
                    "name": entry.target_name + "--" + entry.target_url,
                    "uuid": entry.uuid
                }
                for entry in entry_to_modify
            ]
            return JsonResponse({'status': 'success', 'data': data}, safe=False)
        else:
            return JsonResponse({'status': 'error', 'data': 'no data'})

# 获取搜索任务对应的搜索数据
@csrf_exempt
def GetSearchqueryApi(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        uuid = params['uuid']
        from .models import SearchList
        try:
            search_res = SearchList.objects.filter(uuid=uuid).first()
        except Exception as e:
        # 日志记录异常 e
            return JsonResponse({'status': 'error', 'data': '查询出错'})
        # 检查是否找到匹配的记录
        if search_res:
            return JsonResponse({'status': 'success','data':search_res.request_body})
        else:
            return JsonResponse({'status': 'error', 'data': 'no data'})
        
@csrf_exempt
def GetTaskRestartApi(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        has_restart = 0
        from .models import SearchList
        for task_uuid in params['all_uuid']:
            task = SearchList.objects.filter(uuid=task_uuid).first()
            if task:
                TimingSearch(json.loads(task.request_body))
                has_restart +=1
            else:
                continue

        if has_restart == 0:
            return JsonResponse({'status': 'Failed', 'data': 'no task need to restart'})

        return JsonResponse({'status': 'Succeed', 'data': 'Restarted '+has_restart+' tasks'})