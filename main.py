# This is a sample Python script.
import sys
import json


def export(file):
    with open(file, 'r') as f:
        temp = json.loads(f.read())

        postman = {
            "info": {
                "name": temp['projectInfo']['projectName'],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": group(temp['apiGroupList']),
            "auth": {
                "type": "bearer"
            },
            "variable": [
                {
                    "key": "host",
                    "value": "127.0.0.1:8000"
                }
            ]
        }

        with open('postman.json', 'w') as w:
            w.write(json.dumps(postman))


def group(data):
    temp = []
    for v in data:
        post = {
            "name": v['groupName'],
        }
        if "apiGroupChildList" in v:
            post['item'] = group(v['apiGroupChildList'])
        elif 'apiList' in v:
            post['item'] = apiList(v['apiList'])

        temp.append(post)

    return temp


def apiList(list):
    temp = []

    for v in list:
        info = v['baseInfo']
        api = {
            "name": info['apiName'],
            "request": {
                "method": getRequestType(info['apiRequestType']),
                "header": [],
                # "body": {}, request method post|put
                "url": {
                    "raw": "{{host}}" + info['apiURI'],
                    "host": [
                        "{{host}}"
                    ],
                    "path": [x for x in info['apiURI'].split('/') if x != ''],
                    # "query": [],  # request method get
                }
            },
            "response": []
        }

        request = v['requestInfo']

        if info['apiRequestType'] == 1:
            api['request']['query'] = getRequestQuery(request)
        else:
            params_type = info['apiRequestParamType']
            # 0 formdata 1 json 2 xml,3 raw,4 binary
            modes = {
                0: "formdata",
                1: "json",
                2: "xml",
                3: "raw",
                4: "binary",
            }
            mode = modes.get(params_type, 0)
            body = {
                "mode": mode,
                mode: getRequestQuery(request, False)
            }
            api['request']['body'] = body

        # api['response'] = {
        #     "name": info['apiName'],
        #     "originalRequest": {
        #         "$ref": "#/definitions/request"
        #     },
        #     "body": json.dumps(getResponse(v['resultInfo'])),
        #     "status": "OK",
        #     "code": 200,
        # }

        temp.append(api)

    return temp


def getResponse(resultInfo):
    response = {}

    for result in resultInfo:
        if "childList" in result:
            value = getResponse(result['childList'])
        else:
            if "paramValue" in result:
                value = result['paramValue']
            else:
                value = ""

        response[result['paramKey']] = value

    return response


def getRequestQuery(request, is_query=True):
    body = []
    for q in request:
        query = {
            "key": q['paramKey'],
            "value": q['paramValue'],
        }

        if q['paramNote']:
            query['description'] = q['paramNote']

        if not is_query:
            query['disabled'] = False
            query['type'] = "file" if q['paramType'] == '1' else "text"   # 类型 0=text,1=文件

        body.append(query)

    return body


def getRequestType(type):
    types = {
        0: "POST",
        1: "GET",
        2: "PUT",
        3: "DELETE",
        4: "HEAD",
        5: "OPTIONS",
        6: "PATCH",
    }

    return types.get(type, 1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        path = input("请输入eolinker.json文件:")

        try:
            export(path.strip())
            sys.exit(0)
        except EOFError:
            print('error')
            pass
        pass
