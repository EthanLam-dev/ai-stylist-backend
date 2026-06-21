from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI 
import os
from dotenv import load_dotenv
import traceback
import uvicorn

# 載入 .env 檔案中的環境變數
load_dotenv(override=True)

app = FastAPI()

# 設定 CORS (允許前端跨網域連線)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🌟 1. 安全性升級：金鑰管理
# 系統會優先尋找 .env 裡面的 OPENROUTER_API_KEY。
# 如果找不到，才會暫時使用後面那段字串（強烈建議你未來把它移到 .env 裡）
# ==========================================
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key or "你的真實" in api_key:
    print("❌ 警告：未偵測到有效的 API 金鑰！")
else:
    print("✅ 金鑰載入成功，準備連線 OpenRouter！")

# 🌟 2. 穩定性升級：加入 timeout=30.0 避免請求卡死
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key, timeout=30.0)

class ChatRequest(BaseModel):
    user_message: str

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            # 🌟 3. 核心修復：使用最新的正確模型 ID，解決 400 錯誤
            model="liquid/lfm-2.5-1.2b-instruct:free", 
            messages=[
                {
                    "role": "system", 
                    # 🌟 4. 人設升級：對齊前端的「生物學伴」風格
                    "content": "你是一位專屬的「生物學伴」，擁有豐富的生物學、醫學與生態知識。請用親切、鼓勵且啟發式的語氣回答，就像一位充滿熱情的年輕科學家在跟朋友聊天。嚴格使用繁體中文。適當使用 Markdown (粗體、清單) 讓排版更易讀，並可加入少量 Emoji 讓對話更生動。"
                },
                {"role": "user", "content": request.user_message}
            ]
        )
        return {
            "status": "success",
            "reply": response.choices[0].message.content
        }
    except Exception as e:
        print("❌ 發生錯誤：")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "後端已啟動"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)