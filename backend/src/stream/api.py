# import json
# import asyncio
# from fastapi import APIRouter, Query
# from fastapi.responses import StreamingResponse

# router = APIRouter(prefix="/stream", tags=["stream"])

# async def mock_ai_sdk_streamer():
#     """
#     Mock streaming function to emulate the AI SDK SSE output.
#     """
#     message_id = "1f92e54a-9732-4191-9d33-04f40b616009"
#     text_id = "text-ff36ffdd-4d2b-fb9d-8a2a-5607f1b3679e_us-east-1"
#     deltas = ["Hello! ", "How ", "can ", "I ", "assist ", "you ", "today?"]

#     # Start of message
#     # yield 'data: ' + json.dumps({"type": "start", "messageId": message_id}) + "\n\n"
#     # await asyncio.sleep(0.1)

#     # yield 'data: ' + json.dumps({"type": "start-step"}) + "\n\n"
#     # await asyncio.sleep(0.1)

#     yield 'data: ' + json.dumps({"type": "text-start", "id": text_id}) + "\n\n"
#     await asyncio.sleep(0.1)

#     # Send each token as a delta
#     for delta in deltas:
#         yield 'data: ' + json.dumps({"type": "text-delta", "id": text_id, "delta": delta}) + "\n\n"
#         await asyncio.sleep(0.2)  # simulate real-time streaming

#     # # End of text
#     # yield 'data: ' + json.dumps({"type": "text-end", "id": text_id}) + "\n\n"
#     # await asyncio.sleep(0.1)

#     # yield 'data: ' + json.dumps({"type": "finish-step"}) + "\n\n"
#     # await asyncio.sleep(0.1)

#     # yield 'data: ' + json.dumps({"type": "finish"}) + "\n\n"
#     # await asyncio.sleep(0.1)

#     # # Mock data usage
#     # yield 'data: ' + json.dumps({
#     #     "type": "data-usage",
#     #     "data": {
#     #         "inputTokens": 791,
#     #         "outputTokens": 9,
#     #         "totalTokens": 800,
#     #         "reasoningTokens": 0,
#     #         "context": {
#     #             "outputMax": 4096,
#     #             "combinedMax": 8192,
#     #             "totalMax": 8192,
#     #             "maxOutput": 4096,
#     #             "maxTotal": 8192
#     #         },
#     #         "costUSD": {
#     #             "inputUSD": 0.001582,
#     #             "outputUSD": 0.00009,
#     #             "totalUSD": 0.001672,
#     #             "inputTokenUSD": 0.001582,
#     #             "outputTokenUSD": 0.00009
#     #         },
#     #         "modelId": "xai/grok-2-vision-1212"
#     #     }
#     # }) + "\n\n"
#     # await asyncio.sleep(0.1)

#     # Signal completion
#     # yield 'data: [DONE]\n\n'

# @router.post("/")
# async def stream_response(protocol: str = Query("data")):
#     """
#     Streaming endpoint using mock AI SDK data.
#     """
#     headers = {
#         "Content-Type": "text/event-stream",  # standard SSE
#         "Cache-Control": "no-cache",
#         "Connection": "keep-alive",
#         "x-vercel-ai-data-stream": "v1"
#     }
#     return StreamingResponse(mock_ai_sdk_streamer(), headers=headers)



import json
import asyncio
from fastapi import APIRouter, Query,Request,HTTPException
from fastapi.responses import StreamingResponse
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()


# class UserPrompt(BaseModel):
#     msg:str

router = APIRouter(prefix="/stream", tags=["stream"])

async def mock_ai_sdk_streamer(msg:str):
    """
    Mock streaming function to emulate the AI SDK SSE output.
    """
    all_messages = []
    all_messages.append(msg)
    client=genai.Client()
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=[all_messages]
    )

    # message_id = "1f92e54a-9732-4191-9d33-04f40b616009"
    # deltas = ["Hello! ", "How ", "can ", "I ", "assist ", "you ", "today?"]

    # Start of message
    # yield 'data: ' + json.dumps({"type": "start", "messageId": "22332"}) + "\n\n"
    # await asyncio.sleep(0.1)

    # yield 'data: ' + json.dumps({"type": "start-step"}) + "\n\n"
    # await asyncio.sleep(0.1)

    yield 'data: ' + json.dumps({"type": "text-start", "id": "23224"}) + "\n\n"
    # await asyncio.sleep(0.1)

    # Send each token as a delta
    for chunk in response:
        print(chunk.text)
        yield 'data: ' + json.dumps({"type": "text-delta", "id": "23224", "delta": str(chunk.text)}) + "\n\n"
        # await asyncio.sleep(0.2)  # simulate real-time streaming

    # # End of text
    # yield 'data: ' + json.dumps({"type": "text-end", "id": "2"}) + "\n\n"
    # await asyncio.sleep(0.1)

    # yield 'data: ' + json.dumps({"type": "finish-step"}) + "\n\n"
    # await asyncio.sleep(0.1)

    # yield 'data: ' + json.dumps({"type": "finish"}) + "\n\n"
    # await asyncio.sleep(0.1)

    # # Mock data usage
    # yield 'data: ' + json.dumps({
    #     "type": "data-usage",
    #     "data": {
    #         "inputTokens": 791,
    #         "outputTokens": 9,
    #         "totalTokens": 800,
    #         "reasoningTokens": 0,
    #         "context": {
    #             "outputMax": 4096,
    #             "combinedMax": 8192,
    #             "totalMax": 8192,
    #             "maxOutput": 4096,
    #             "maxTotal": 8192
    #         },
    #         "costUSD": {
    #             "inputUSD": 0.001582,
    #             "outputUSD": 0.00009,
    #             "totalUSD": 0.001672,
    #             "inputTokenUSD": 0.001582,
    #             "outputTokenUSD": 0.00009
    #         },
    #         "modelId": "xai/grok-2-vision-1212"
    #     }
    # }) + "\n\n"
    # await asyncio.sleep(0.1)

    # Signal completion
    yield 'data: [DONE]\n\n'

@router.post("/")
async def stream_response(request:Request):
 try:
    """
    # Streaming endpoint using mock AI SDK data.
    """
    body = await request.json()
    print(body)
    msg = body['msg']['parts'][0]['text']
    print(msg)
    headers = {
        "Content-Type": "text/event-stream",  # standard SSE
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "x-vercel-ai-data-stream": "v1",
    }
    return StreamingResponse(mock_ai_sdk_streamer(msg), headers=headers)
 except Exception as e:
      raise HTTPException(
            # status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

