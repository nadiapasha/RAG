import timeit
import argparse
from rag.pipeline import build_rag_pipeline
import json
import time
import warnings
import re

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
import uvicorn
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings('ignore', category = DeprecationWarning)

##############
app = FastAPI()

# Configure templates
templates = Jinja2Templates(directory="template")

app.mount("/static", StaticFiles(directory="static"), name="static")

################

def get_rag_response(query, chain, debug = False):
    result = chain.query(query)
 
    document_info = str(result.metadata)
    find = re.findall(r"'page_label': '[^']*', 'file_name': '[^']*'", document_info)

    
    info = find
    print("Relevant pages: ",info)
    return str(result), info





parser = argparse.ArgumentParser()
        
parser.add_argument('--debug',
                            action ='store_true',
                            help = 'Enable debug mode')
        
args = parser.parse_args()
        
        
rag_chain = build_rag_pipeline(args.debug)
    

    
#     ##########################
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse('index.html',{'request':request})  

@app.post("/get_answer")
async def get_answer(request: Request, question: str = Form(...)):
    print(question)
    #question = "your question?"
    answer, relevant_docs = get_rag_response(question, rag_chain, args.debug)
    response_data = jsonable_encoder(json.dumps({'answer': answer, 'relevant_docs':relevant_docs}))
    
    res = Response(response_data)
    #return res
    return JSONResponse({'answer': answer, 'relevant_docs':relevant_docs})
    


if __name__ == '__main__':
    uvicorn.run("app:app", host = '0.0.0.0',port = 8001, reload = True)
        
    