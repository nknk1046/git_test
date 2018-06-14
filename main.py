# -*- coding: utf-8 -*-
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from bottle import route, run, template, redirect, request
import http.client, urllib.parse, uuid, json

#translate text apiの接続情報
TRANS_ACCESS_KEY = "b2119fbe19bc40d0973696ed7c00e730"
HOST = 'api.cognitive.microsofttranslator.com'
PATH = '/translate?api-version=3.0'

# Translate to JAPANESE
PARAM = "&to=ja";
TEXT = 'Hello World！'

def translate (content):
    headers = {
        'Ocp-Apim-Subscription-Key': TRANS_ACCESS_KEY,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    conn = http.client.HTTPSConnection(HOST)
    conn.request ("POST", PATH + PARAM, content, headers)
    response = conn.getresponse ()
    return response.read ()

#読みやすい形式で出力する
#output = json.dumps(json.loads(result), indent=4, ensure_ascii=False)
#print (output)

table_service = TableService(connection_string='DefaultEndpointsProtocol=https;AccountName=k1cosmos;AccountKey=rvw8KdHLNumJp6q6JpcDSbeI1oaBNrwM7iJ1r9fVD0WeJHkL1soQAubah1J35zlV6UCgGUArvm13U3VTsFQfWQ==;TableEndpoint=https://k1cosmos.table.cosmosdb.azure.com:443/')
@route("/")
def index():
    todo_list = get_todo_list()
    #return template("Trans_test/index", todo_list=todo_list)
    return template("Trans_test/top", todo_list=todo_list)

# methodにPOSTを指定して、add関数を実装する
@route("/add", method="POST")
def add():
    todo = request.forms.getunicode("todo_list")
    requestBody = [{
    'Text' : todo,
    }]
    content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')
    result = translate (content)
    #必要な値を取り出す
    json_dict = json.loads(result)
    print(json_dict)
    print(json_dict[0]["translations"][0]["text"])
    trans_result = json_dict[0]["translations"][0]["text"]
    save_todo(trans_result)
    return redirect("/")

# @routeデコレータの引数で<xxxx>と書いた部分は引数として関数に引き渡すことができます。
# intは数字のみ受け付けるフィルタ
@route("/delete/<todo_id>")
def delete(todo_id):
    delete_todo(todo_id)
    return redirect("/")

def get_todo_list():
    todo_list = []
    tasks = table_service.query_entities('tasktable2', filter="PartitionKey eq 'tasksSeattle2'")
    for task in tasks:
        todo_list.append({"id": task.RowKey,"todo": task.description})
    #todo_list.append({"todo": task.description})
    #print(todo_list)
    return todo_list

def save_todo(todo):
    task = {'PartitionKey': 'tasksSeattle2', 'RowKey': '003', 'description' : todo, 'priority' : 200}
    table_service.insert_entity('tasktable2', task)

def delete_todo(todo_id):
    #todo_tmp = "003"
    print(todo_id)
    table_service.delete_entity('tasktable2', 'tasksSeattle2', todo_id)

#テスト用のサーバをlocalhost:8080で起動する
#run(host="localhost", port=8080, debug=True, reloader=True)

#k1webappで起動
#run(host="k1webapp.azurewebsites.net", port=80, debug=True, reloader=True)

#Webapp実行の場合
#if __name__ == '__main__':
#    app.run()