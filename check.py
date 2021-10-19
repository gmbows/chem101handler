import requests, json
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

user_token = "" #user token here

h = "Host: api.101edu.io\n\
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0\n\
Accept: application/json, text/plain, */*\n\
Accept-Language: en-US,en;q=0.5\n\
Accept-Encoding: gzip, deflate, br\n\
Referer: https://app.101edu.co/\n\
platform: WEB\n\
project: CHEM101_REACT_NATIVE\n\
version: 3.12.3\n\
token: {0}\n\
Origin: https://app.101edu.co\n\
DNT: 1\n\
Content-Type: application/json;charset=utf-8\n\
Connection: keep-alive\n\
Sec-Fetch-Dest: empty\n\
Sec-Fetch-Mode: no-cors\n\
Sec-Fetch-Site: cross-site\n\
TE: trailers\n\
Pragma: no-cache\n\
Cache-Control: no-cache".format(user_token)

def conv(headers):
	headers = {} 

	#convert raw string to dict headers
	for line in h.split("\n"):
		headers.update({line.split(": ")[0] : line.split(": ")[1]})
		
	return headers
		
headers = conv(h)

check_url = "https://api.101edu.io/api/assignment/feed?courseIds=610ac07042e9f91d98c5b623&assignmentTypes=IN_CLASS%2CATTENDANCE&calculateGrade=true&indexes=smart&page=0&size=10"
assignment_url = "https://api.101edu.io/api/assignment/{0}/view"
answer_url = "https://api.101edu.io/api/answer"


def get_assignment(id):
	a_url = assignment_url.format(id)
	assignment = get_page(a_url)
	return json.loads(assignment)

def get_last_assignment():
	check = get_page(check_url)
	write_page("dashboard.json",check)
	check_json = json.loads(check)
	return check_json["data"]["items"][0]

def get_page(this_url):
	page = requests.get(this_url,headers=headers)
	data = page.content
	return data

def write_page(filename,data):
	f = open(filename,"wb+")
	f.write(data)
	f.close()
	
def submit_ans():
	x = requests.post(answer_url,headers=headers,data=data)
	write_page("test.json",x.content)

def write_last_assignment():
	id = get_last_assignment()["id"]
	assignment_page = get_page(assignment_url.format(id))

	write_page("last_assignment.json",assignment_page)

pages = 0

mixer.init()

sleeping = False

while(True):
	last = get_last_assignment()
	write_last_assignment()
	if(last["live"] == True):
		sleeping = False
		assignment = get_assignment(last["id"])
		if(assignment["data"]["grade"]["correctPoints"] == assignment["data"]["points"]):
			if not sleeping:
				print("An assignment is active, but has been completed, sleeping until new assignment is posted")
				sleeping = True
			time.sleep(20)
			continue

		#play notification sound
		mixer.music.load("notif.wav")
		mixer.music.play()

		print("New assignment is active and incomplete")
		print("Title:",assignment["data"]["name"])
		for problem in assignment["data"]["problems"]:
			try:
				print("Question",str(problem["position"])+": ",json.loads(problem["answerDescriptor"][1:-1])["choiceIds"])
			except:
				print("Question",str(problem["position"])+": ",problem["answerHash"])
		time.sleep(20)
	else:
		if(not sleeping):
			print("No active assignments, sleeping until new assignment is posted")
		sleeping = True
