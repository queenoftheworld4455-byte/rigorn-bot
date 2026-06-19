# =========================
# GET PHOTO FILE ID
# =========================
@dp.message(F.photo)
async def get_photo_id(message: Message):

    photo_id = message.photo[-1].file_id

    await message.answer(
        f"📸 Photo File ID:\n\n{photo_id}"
    )

    print("PHOTO FILE ID:")
    print(photo_id)

    