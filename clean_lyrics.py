
import json
import os

PATH_TO_FOLDER="./eminem"
DESTINATION_FOLDER="%s_clean" % PATH_TO_FOLDER


def clean_lyrics(lyrics_array):
    #print(lyrics_array)
    result = []
    for line in lyrics_array:
        if line != "" and line[0] != "[" :
            #print(line)
            result.append(line)
    return result

def create_folder(path):
    try:  
        os.mkdir(path)
    except FileExistsError:  
        return True
    except:  
        return False
    else:  
        return True

def write_file(file_name, data):
    try:
        with open(file_name, 'w') as f:
            for item in data:
                f.write("%s\n" % item)
    except:
        return False
    else:  
        return True

for filename in os.listdir(PATH_TO_FOLDER):
    if create_folder(DESTINATION_FOLDER):
        print("created folder")
        if filename[-5:] == ".json" and filename[:7] == "lyrics_" :
            print("found json file: %s" % filename)
            print("short %s" % filename[7:-5])
            with open("%s/%s" % (PATH_TO_FOLDER, filename)) as json_file:  
                data = json.load(json_file)
                data = data["songs"][0]["lyrics"]
                if data == None:
                    print("skipping, no lyrics")
                    continue
                data = clean_lyrics(data.split("\n"))
                to_write = "%s/%s.txt" % (DESTINATION_FOLDER, filename[7:-5])
                if write_file(to_write, data):
                    print("succesfully written %s" % to_write )
                else:
                    print("error writing %s" % to_write)