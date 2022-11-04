import json
from utils import print_out


class Compare_Data:

    def __init__(self):
        self.applied_mappings = {}
        self.to_update = {}
        self.to_create = {}
        self.to_delete = {}
        self.data = {}
        self.map = None
        self.load_map()

    def load_map(self):
        # load the map config for mapping src with dest
        with open("map_config.json") as file:
            self.map = json.load(file)

    def if_src_dest_list(self, src, dest, parent):
        # if field in src and dest are array ,iterate thru the array calling the map method

        to_create = []
        to_delete = []
        while len(src) or len(dest):
            if len(src):
                data1 = src.pop(0)
            else:
                data1 = None
            if len(dest):
                data2 = dest.pop(0)
            else:
                data2 = {}
            
            if data1 and data2:
                self.match_src_dest(data1, data2, parent=parent)
            elif data1 and not data2:
                for key in data1:
                    dest_key = self.map[parent+key]
                    if "." in dest_key:
                        dest_key = dest_key.split(".")[-1]
                    data2[dest_key] = data1[key]
                to_create.append(data2)
            elif data2 and not data1:
                to_delete.append(data2)
        if to_create:
            self.to_create[self.map[parent[:-1]]] = to_create
        if to_delete:
            self.to_delete[self.map[parent[:-1]]] = to_delete

    def match_src_dest(self, obj, dest, parent=""):
        # compare and map the fields in src with fields in dest
        src_result = {}
        dest_result = {}
        for key in obj:
            parent_key = parent + key
            if self.map.get(parent_key):
                
                dest_key = self.map.get(parent_key)
                if "." in dest_key:
                    dest_key = dest_key.split(".")[-1]
                
                if isinstance(obj[key], list) and isinstance(dest[dest_key], list):
                    self.if_src_dest_list(obj[key], dest[dest_key], parent=parent_key+'.')

                elif isinstance(obj[key], dict) and isinstance(dest[self.map[key]], dict):
                    self.match_src_dest(obj[key], dest[self.map[key]], parent=parent_key+'.')

                elif not isinstance(obj[key], list)  and not isinstance(obj[key], dict) and \
                    '.' in self.map[parent_key] and (isinstance(dest[dest_key], dict)):
                    
                    self.match_src_dest({key: obj[key]}, dest[self.map[parent_key].split('.')[-2]])
                else:
                    dest_result[dest_key] =  dest.get(dest_key)
                    src_result[key] = obj[key]

                    self.applied_mappings[parent_key] = self.map[parent_key]
                    
            else:
                if isinstance(obj[key], list) or isinstance(obj[key], dict):
                    if isinstance(obj[key], list):
                        obj[key] = obj[key][0]
                    self.match_src_dest(obj[key], dest, parent=key+".")
                # else:
                #     print(f"There is no mapping found for the Key: {key}")
        
        self.compare_data_generate_diff(src_result, dest_result, parent=parent)

        return self.applied_mappings, self.to_update, self.to_create, self.to_delete
    
    def compare_data_generate_diff(self, src, dest, parent=None):
        # generate diff and path data
        to_update = {}
    
        for k1, k2 in zip(src, dest):
            if src[k1] != dest[k2] and k1 != "id":
                if parent:
                    parent_key = parent+k1
                    print_out("red", f"Record Mismatch: \n\t{parent_key}: {src[k1]} => source \n\t{self.map[parent_key]}: {dest[k2]} => destination")

                else:
                    print_out(f"red", f"Record Mismatch: \n\t{k1}: {src[k1]} => source \n\t{self.map[k1]}: {dest.get(k2)} => destination")

                to_update[k2] = src[k1]
        if dest.get("id"):
            to_update["identity"] = dest["id"]
        if parent and self.map.get(parent[:-1]):

            if self.to_update.get(self.map[parent[:-1]]):
                self.to_update[self.map[parent[:-1]]].append(to_update)
            else:
                self.to_update[self.map[parent[:-1]]] = [to_update]
        else:
            self.to_update.update(to_update)

