# =========================
# GET PHOTO FILE ID
# =========================

@dp.message(F.photo)
async def get_photo_id(message: Message):

    file_id = message.photo[-1].file_id

    print("PHOTO FILE ID:")
    print(file_id)

    await message.answer(
        f"PHOTO FILE ID:\n\n{file_id}"
    )