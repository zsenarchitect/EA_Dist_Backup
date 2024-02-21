"""pack this exe using python 3"""
import time
import traceback
import os
import datetime
import json

def log_error(error):
    error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
    error_file = "{}\Documents\EnneadTab Settings\Local Copy Dump\error_log.txt".format(os.environ["USERPROFILE"])

    with open(error_file, "w") as f:
        f.write(error)

    if os.environ["USERPROFILE"].split("\\")[-1] == "szhang":
        os.startfile(error_file)

        
try:
    from PIL import Image
    import requests
except:
    pass

try:
    pass
except:
    error = traceback.format_exc()
    log_error(error)

##############################################################
HOSTER_FOLDER = "L:\\4b_Applied Computing"
MISC_FOLDER = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Misc".format(HOSTER_FOLDER)
def get_api_key(key_name):
    
    file_path = r"{}\EA_API_KEY.json".format(MISC_FOLDER)

    data = read_json_as_dict(file_path)
    return data.get(key_name, None)



def read_json_as_dict(filepath, use_encode=False, create_if_not_exist = False):
    """get the data saved in json as dict

    Args:
        filepath (_type_): _description_
        use_encode (bool, optional): for Chinese char file it might need encoding. Defaults to False.

    Returns:
        dict | None: _description_
    """
    
    with open(filepath, encoding='utf8') as f:
        data = json.load(f)
    return data

def read_json_as_dict_in_dump_folder(file_name, use_encode=False, create_if_not_exist=False):
    """direct access the json file from dump folder

    Args:
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = get_EA_dump_folder_file(file_name)
    return read_json_as_dict(filepath, use_encode, create_if_not_exist)


def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\Documents\EnneadTab Settings\Local Copy Dump\{}".format( os.environ["USERPROFILE"], file_name)

def get_formatted_current_time():
    """-->2023-05-16_11-33-55"""
    now = datetime.datetime.now()
    return get_formatted_time(now)


def get_formatted_time(input_time):
    #  if input is float, convert to datetime object first:
    if isinstance(input_time, float):
        input_time = datetime.datetime.fromtimestamp(input_time)
    
    year, month, day = '{:02d}'.format(input_time.year), '{:02d}'.format(input_time.month), '{:02d}'.format(input_time.day)
    hour, minute, second = '{:02d}'.format(input_time.hour), '{:02d}'.format(input_time.minute), '{:02d}'.format(input_time.second)
    return "{}-{}-{}_{}-{}-{}".format(year, month, day, hour, minute, second)


def get_readable_time(time_in_seconds):

    
    
    
    time_in_seconds = int(time_in_seconds)
    if time_in_seconds < 60:
        return "{}s".format(time_in_seconds)
    if time_in_seconds < 3600:
        mins = int(time_in_seconds/60)
        secs = time_in_seconds%60
        return "{}m {}s".format(mins, secs)
    
    
    # hours = int(time_in_seconds/3600)
    # mins = time_in_seconds%60
    # secs = time_in_seconds%60
    
    hours = time_in_seconds // 3600
    mins = (time_in_seconds % 3600) // 60
    secs = time_in_seconds % 60
    return "{}h {}m {}s".format(hours, mins, secs)

###############################################################################
def get_token():
    return get_api_key("miro_oauth")

class ShapeStyle:
    New = "cross", "#48bbdb"
    Update = "star", "#ffa500"
    Duplicate = "hexagon", "#f94449"

    @classmethod
    def get_valid_shapes(cls):
        return [ShapeStyle.New[0], 
                ShapeStyle.Update[0], 
                ShapeStyle.Duplicate[0]]

    
class Miro:
    def __init__(self, board_id_or_url):
        if "board/" in board_id_or_url:
            board_id_or_url = board_id_or_url.split("board/")[-1].replace("/", "")
        self.board_id = board_id_or_url

        self.token = get_token()


    @staticmethod
    def get_all_boards_info(keyword = None):
        url = "https://api.miro.com/v2/boards"
        if keyword:
            url = url + "?query={}".format(keyword)

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(get_token())
        }

        response = requests.get(url, headers=headers)


        # print(response.text)
        return response.json()
        
    @staticmethod
    def create_board(board_name,
                    description = ""):
        
        url = "https://api.miro.com/v2/boards"

        payload = {
            "name": board_name,
            "description": description
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer {}".format(get_token())
        }

        response = requests.post(url, json=payload, headers=headers)

        return Miro(response.json()["id"])



    @staticmethod
    def get_board(board_id_or_url):

        if "board/" in board_id_or_url:
            board_id_or_url = board_id_or_url.split("board/")[-1].replace("/", "")

        return Miro(board_id_or_url)




    def create_frame(self,
                     frame_data,
                     position,
                     geometry):
        pass

    def update_frame(self,
                     frame_id,
                     frame_data,
                     position = None,
                     geometry = None):
        pass
        # should also rename the frame with update timestamp

    def get_frame_by_name(self, frame_name):
        return self.find(frame_name, "frame")



    
    def get_frame_children(self,
                           frame_or_frame_id):
        if frame_or_frame_id.has_key("id"):
            frame_id = frame_or_frame_id['id']
        else:
            frame_id = frame_or_frame_id
        


        url = "https://api.miro.com/v2/boards/{}/items?parent_item_id={}".format(self.board_id,
                                                                                 frame_id)

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(self.token)
        }

        response = requests.get(url, headers=headers)

 
        return response.json()



    def create_images(self, creation_datas):
        url = "https://api.miro.com/v2/boards/{}/images".format(self.board_id)

        
        headers = {
            "Authorization": "Bearer {}".format(self.token)
        }
        files = []
        for creation_data in creation_datas:
            image_full_path = creation_data["full_path"]
            position = creation_data["position"]
            width = creation_data["width"]
            title = creation_data["title"]
            
            file = (
                "resource",
                (os.path.basename(image_full_path), open(image_full_path, "rb"), "image/jpg"),
            ),
            (
                "data",
                (
                    None,
                    json.dumps(
                        {
                            "title": title,
                            "position": {
                                "x": position[0],
                                "y": position[1],
                            },
                            "geometry": {
                                "width": width,
                                "rotation": 0,
                            }
                        }
                    ),
                    "application/json",
                ),
            )

            files.append(file)
        
        response = requests.post(url, headers=headers, data={}, files=files)
        print (response.text)
    
    def create_image(self,
                     image_full_path,
                     position,
                     width = None,
                     image_title = None, 
                     parent = None):

        url = "https://api.miro.com/v2/boards/{}/images".format(self.board_id)


        title = image_title if image_title else image_full_path.split("/")[-1]

        creation_data ={
                    "title": title,
                    "position": {
                                "x": position[0],
                                "y": position[1]
                    }
                }
        if width:
            creation_data.update({"geometry": {"width": width}})

        if parent:
            creation_data.update({"parent": {"id": parent}})
        files = [
            (
                "resource",
                (os.path.basename(image_full_path), open(image_full_path, "rb"), "image/jpg"),
            ),
            (
                "data",
                (
                    None,
                    json.dumps(
                        creation_data
                    ),
                    "application/json",
                ),
            ),
        ]

        headers = {
            "Authorization": "Bearer {}".format(self.token)
        }

        response = requests.post(url, headers=headers, data={}, files=files)
        # print (response.text)

        return response.json()

        

    def update_image(self,
                     image_id,
                     image_full_path,
                     image_title = None,
                     position = None,
                     width = None,
                     parent = None):
        
        url = "https://api.miro.com/v2/boards/{}/images/{}".format(self.board_id,
                                                                   image_id)


        title = image_title if image_title else image_full_path.split("/")[-1]
        

        creation_data ={
                            "title": title,
        }

        if position:
            creation_data.update({"position": {"x": position[0], "y": position[1]}})

        if width:
            creation_data.update({"geometry": {"width": width}})

        if parent:
            creation_data.update({"parent": {"id": parent}})


        files = [
            (
                "resource",
                (os.path.basename(image_full_path), open(image_full_path, "rb"), "image/jpg"),
            ),
            (
                "data",
                (
                    None,
                    json.dumps(
                        creation_data
                    ),
                    "application/json",
                ),
            ),
        ]

        headers = {
            "Authorization": "Bearer {}".format(self.token)
        }

        response = requests.patch(url, headers=headers, data={}, files=files)
        # print (response.text)

        return response.json()

    def create_mark(self,
                    position,
                    width,
                    style,
                    text = ""):

        shape, color = style
        
        url = "https://api.miro.com/v2/boards/{}/shapes".format(self.board_id)

        payload = {
            "data": {
                "shape": shape
            },
            "style": { "fillColor": color ,
                      "fillOpacity" : "1.0"},
            "position": {
                "x": position[0],
                "y": position[1]
            },
            "geometry": { "width": width,
                         "height": width}
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer {}".format(self.token)
        }

        response = requests.post(url, json=payload, headers=headers)
        print("create a {}".format(shape))
        # print(response.text)


        
    def create_sticky_note(self,
                           sticky_note_data,
                           position,
                           geometry,
                           parent = None):
        pass


    def create_connection(self,
                          start_id,
                          end_id,
                          connection_text = None):

        url = "https://api.miro.com/v2/boards/{}/connectors".format(self.board_id)

        payload = {
            "startItem": {
                "id": start_id,
                "snapTo": "auto"
            },
            "endItem": {
                "id": end_id,
                "snapTo": "auto"
            }
        }

        if connection_text:
            payload.update({"captions": [{ "content": connection_text }]})
            
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer {}".format(self.token)
        }

        response = requests.post(url, json=payload, headers=headers)

        # print(response.text)

        return response.json()["id"]


    def highlight_frames(self, frame_ids):
        if not isinstance(frame_ids, list):
            frame_ids = [frame_ids]


        for frame_id in frame_ids:
            pass

    def purge_markers(self):
        url = "https://api.miro.com/v2/boards/{}/items?limit=50&type=shape".format(self.board_id)

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(self.token)
        }

        cursor = None
        makrer_ids = []
        while True:
            if cursor:
                final_url = url + "&cursor={}".format(cursor)
            else:
                final_url = url
                

            response = requests.get(final_url, headers=headers)
            for item in response.json()["data"]:
                if item["data"]["shape"] in ShapeStyle.get_valid_shapes():
                    makrer_ids.append(item["id"])
                    
            if "cursor" in response.json():
                cursor = response.json()["cursor"]
            else:
                break

        if len(makrer_ids)==0:
            print ("there is no marker on the board")
            return None
        
        for i, id in enumerate(makrer_ids):
            print ("delete {}/{} marker".format(i+1, len(makrer_ids)))
            

            url = "https://api.miro.com/v2/boards/{}/shapes/{}".format(self.board_id, id)

            headers = {
                "accept": "application/json",
                "authorization": "Bearer {}".format(self.token)
            }

            response = requests.delete(url, headers=headers)
           

                
    def find_ids_as_dict(self, search_keys = None, type = None):
        """keep looking up as long as ther is a cursor left, exhaust and collect all ids

        Args:
            search_keys (list): _description_
            type (_type_, optional): _description_. Defaults to None.

        Returns:
            dict: a pair dict (search_key, item_id)
        """

        key_map = {"duplicated_item":[],
                   "all":[]}

        if type:
            url = "https://api.miro.com/v2/boards/{}/items?type={}".format(self.board_id, type)
        else:
            url = "https://api.miro.com/v2/boards/{}/items".format(self.board_id)

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(self.token)
        }

        cursor = None
        while True:
            if cursor:
                if type:
                    final_url = url + "&cursor={}".format(cursor)
                else:
                    final_url = url + "?cursor={}".format(cursor)
            else:
                final_url = url

            response = requests.get(final_url, headers=headers)

            
            for item in response.json()["data"]:
                if search_keys:
                    for key in search_keys:
                        item_data = item["data"]
                        title = item_data.get("title", None)
                        if not title:
                            continue
                        if key in title:
                            print ("found {}".format(title))

                            if key not in key_map:
                                key_map[key] = item
                            else:
                                key_map["duplicated_item"].append(item)
                else:
                    key_map["all"].append(item)
                                
            if "cursor" in response.json():
                cursor = response.json()["cursor"]
            else:
                break

        return key_map
    
    def find(self,
             human_name,
             type = None):
        """_summary_

        Args:
            human_name (single): _description_
            type (_type_, optional): _description_. Defaults to None.

        Returns:
            single item, depeden on the input type of human names
        """
 
        print ("searching for {}".format(human_name))
        
        url = "https://api.miro.com/v2/boards/{}/items".format(self.board_id)

        headers = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(self.token)
        }

        response = requests.get(url, headers=headers)

        # print (response.text)


        if response.json()["size"]==0:
            print ("there is nothing on the board")
            return None
        

        for item in response.json()["data"]:
            if type:
                if item["type"] != type:
                    continue

            if human_name in item["data"]["title"]:
                print ("found {}".format(item["data"]["title"]))
                return item

        return None




class CornerLocation:
    TopLeft = "TopLeft"
    TopRight = "TopRight"
    BottomLeft = "BottomLeft"
    BottomRight = "BottomRight"

    @staticmethod
    def get_item_corner(item, location):
        x, y = item["position"]["x"], item["position"]["y"]
        w, h = item["geometry"]["width"], item["geometry"]["height"]
        if location == CornerLocation.TopLeft:
            return (x-w/2, y-h/2)
        elif location == CornerLocation.TopRight:
            return (x+w/2, y-h/2)
        elif location == CornerLocation.BottomLeft:
            return (x-w/2, y+h/2)
        elif location == CornerLocation.BottomRight:
            return (x+w/2, y+h/2)



class MiroListerner(Miro):
    
    def listen(self):
        print ("listening to miro")
        count = 5

        # i want app to run infinitely until window is closed
        while True:
            print ("{} until the listen goes to sleep.".format(get_readable_time(count)))
            time.sleep(1)
            if count <= 0:
                break

            count -= 1
            self.download_data()

    def download_data(self):  
        data = self.find_ids_as_dict(type="shape")
        with open(get_EA_dump_folder_file("miro_download.json"), "w") as f:
            json.dump(data, f, indent=4)

class MiroPusher(Miro):
    pass
##################################################################


def update_revit_sheets_on_miro(sheet_imgs, miro_board_url):
    """_summary_

    Args:
        sheet_imgs (list): a typical img fiel name looks like this folder\\{guid}^{sheetNum}^{sheetName}.jpg
        miro_board_url (_type_): _description_

    Returns:
        _type_: _description_
    """
    miro_board = Miro.get_board(miro_board_url)

    miro_board.purge_markers()

    guid_list = []
    for sheet_img in sheet_imgs:
        guid = sheet_img.split("\\")[-1].split("^")[0]
        guid_list.append(guid)

    key_map = miro_board.find_ids_as_dict(guid_list)

    duplicated_items = key_map.pop("duplicated_item")
    if duplicated_items:
        print ("there are duplicated items")
        for item in duplicated_items:
            corner_location = CornerLocation.get_item_corner(item, CornerLocation.TopLeft)
            miro_board.create_mark(corner_location,
                               item["geometry"]["width"]*0.2,
                               ShapeStyle.Duplicate)

    
    for i, sheet_img in enumerate(sheet_imgs):
        print ("\n\n### Processs {} of {} sheets".format(i+1, len(sheet_imgs)))
        guid = sheet_img.split("\\")[-1].split("^")[0]
        full_path = sheet_img
        sheet_num = sheet_img.split("\\")[-1].split("^")[1]
        sheet_name = sheet_img.split("\\")[-1].split("^")[2].split(".")[0]
 

        image_title = "[{}]_[{}]_{}".format(sheet_num, sheet_name, guid)
        image = key_map.get(guid, None)


        if not image:
            print("creating image {}".format(image_title))

            img = Image.open(full_path)
            width, height = img.size

            image = miro_board.create_image(full_path,
                                            (i*(width *1.2),0),
                                            image_title=image_title)
            marker_style = ShapeStyle.New
        else:
            image_id = image["id"]
            print("updating image {}".format(image_title))
            image_title = image_title + "[Uploaded at {}]".format(get_formatted_current_time())
            image = miro_board.update_image(image_id, 
                                            full_path,
                                            image_title=image_title)
            marker_style = ShapeStyle.Update


        corner_location = CornerLocation.get_item_corner(image, CornerLocation.TopRight)
        miro_board.create_mark(corner_location,
                               image["geometry"]["width"]*0.1,
                               marker_style)

    print("!!!!!!!!!!!!!! Finish updating miro")

    return miro_board

    

def main():
    data = read_json_as_dict_in_dump_folder("miro.json")
    app, url=  data["app"], data["url"]

    if app == "revit_sheet":
        sheet_imgs = data["images"]
        update_revit_sheets_on_miro(sheet_imgs, url)

    elif app == "rhino_listener":
        # lisnter only download json data, it does not bake.
        # the bake action is handle in rhino when user decide to bake
        miro_board = MiroListerner(url)
        miro_board.listen()

    elif app == "rhino_pusher":
        geos = data["geos"]
        miro_board = MiroPusher(url)
        miro_board.push(geos)



    
if __name__ == "__main__":
    try:
        main()
    except:
        error = traceback.format_exc()
        log_error(error)
        
    # board = Miro.create_board("test")
    # info = Miro.get_all_boards_info("DumpSheet")
    # # info = Miro.get_all_boards_info()

    #print (info)
    # test_board_id = info["data"][0]["id"]
    # print(test_board_id)


    # board = Miro.get_board(test_board_id)
    # print (board)