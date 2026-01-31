import zipfile

for name in zipfile.ZipFile("dist/eden_music_scene-0.1.0-py3-none-any.whl").namelist():
    print(name)
