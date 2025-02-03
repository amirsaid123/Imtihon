import json
import aiofiles


async def save_comment(user_info, comment):
    async with aiofiles.open("/home/amirsaid/PycharmProjects/Anonim_chat/comments.json", "r", encoding="utf-8") as f:
        contents = await f.read()
        comments_data = json.loads(contents)

    comments_data.append({
        "user_id": user_info.id,
        "username": user_info.username,
        "full_name": user_info.full_name,
        "comment": comment
    })

    async with aiofiles.open("/home/amirsaid/PycharmProjects/Anonim_chat/comments.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(comments_data, ensure_ascii=False, indent=4))

