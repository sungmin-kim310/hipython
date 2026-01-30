from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#res = client.responses.create(
#    model = 'gpt-4o-mini',
#    input = [
#        {"role" : "system", "content" : "너는 마케팅 전문가야"},
#        {"role" : "user", "content" : "광고 문구를 작성"}
#    ],
#    temperature=0
#) - 헬퍼 없는 경우

def msg(role, text) :
    msg_src = {"role" : role, "content" : [{"type":"input_text", "text":text}]}
    return msg_src

res = client.responses.create(
    model = 'gpt-4o-mini',
    input = [
        msg("system","너는 마케팅 전문가야"),
        msg("user", "광고 문구를 작성")
        #{"role" : "system", "content" : "너는 취업 전문가야"}, - 헬퍼 없을 경우
        #{"role" : "user", "content" : "광고 문구를 작성"} - 헬퍼 없을 경우
    ],
    temperature=0
)

print(res.output_text)