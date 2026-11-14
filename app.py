import os, time
from collections import defaultdict, deque
from flask import Flask, jsonify, request, send_from_directory
import requests
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=BASE_DIR)
app.config['MAX_CONTENT_LENGTH']=18*1024*1024
SUPABASE_URL=os.environ.get('SUPABASE_URL','').rstrip('/')
SUPABASE_ANON_KEY=os.environ.get('SUPABASE_ANON_KEY','')
GEMINI_API_KEY=os.environ.get('GEMINI_API_KEY','')
GEMINI_MODEL=os.environ.get('GEMINI_MODEL','gemini-3.7-flash')
request_times=defaultdict(deque)
def verify_user(token):
 if not SUPABASE_URL or not SUPABASE_ANON_KEY:return None,'Server authentication is not configured.'
 try:
  r=requests.get(SUPABASE_URL+'/auth/v1/user',headers={'apikey':SUPABASE_ANON_KEY,'Authorization':'Bearer '+token},timeout=12)
  if r.status_code!=200:return None,'Please log in again.'
  return r.json(),None
 except requests.RequestException:return None,'Could not verify your login. Please try again.'
@app.get('/')
def home():return send_from_directory(BASE_DIR,'index.html')
@app.get('/health')
def health():return jsonify({'ok':True,'model':GEMINI_MODEL})
@app.post('/api/chat')
def chat():
 if not GEMINI_API_KEY:return jsonify({'error':'Chatbot server API key is not configured yet.'}),503
 auth=request.headers.get('Authorization','')
 if not auth.startswith('Bearer '):return jsonify({'error':'Please log in to use Asim AI.'}),401
 user,error=verify_user(auth[7:])
 if error:return jsonify({'error':error}),401
 uid=user.get('id','unknown');now=time.time();q=request_times[uid]
 while q and now-q[0]>60:q.popleft()
 if len(q)>=20:return jsonify({'error':'Too many messages in a short time. Please wait one minute.'}),429
 q.append(now)
 payload=request.get_json(silent=True) or {};contents=payload.get('contents')
 if not isinstance(contents,list) or not contents:return jsonify({'error':'Please enter a message.'}),400
 contents=contents[-30:];system_instruction=payload.get('systemInstruction',{})
 endpoint='https://generativelanguage.googleapis.com/v1beta/models/'+GEMINI_MODEL+':generateContent'
 try:
  r=requests.post(endpoint,headers={'Content-Type':'application/json','x-goog-api-key':GEMINI_API_KEY},json={'contents':contents,'systemInstruction':system_instruction,'generationConfig':{'temperature':0.7}},timeout=90)
  try:data=r.json()
  except ValueError:data={}
  if not r.ok:
   message=data.get('error',{}).get('message') or ('Gemini API error: HTTP '+str(r.status_code))
   return jsonify({'error':message}),r.status_code
  parts=data.get('candidates',[{}])[0].get('content',{}).get('parts',[]);answer=''.join(p.get('text','') for p in parts)
  if not answer:return jsonify({'error':'Gemini returned an empty response. Please try again.'}),502
  return jsonify({'text':answer,'model':GEMINI_MODEL})
 except requests.Timeout:return jsonify({'error':'Gemini response took too long. Please try again.'}),504
 except requests.RequestException:return jsonify({'error':'Could not connect to Gemini. Please try again.'}),502
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT','10000')))
