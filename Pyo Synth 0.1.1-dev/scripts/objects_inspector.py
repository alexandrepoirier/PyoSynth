from pyo import *
import inspect, pickle, os

# Write to a file in the current working directory
OUTPUT_FILE = os.path.join(os.getcwd(), "audio_rate_params_dict.txt")

def get_args_doc(obj):
    text = eval(obj).__doc__
    pos = text.find(":Args:")
    if pos != -1:
        pos1 = text.find("\n", pos) + 1
        pos2 = text.find(">>>", pos1)
        return text[pos1:pos2]
    else:
        return ""

def is_audio_rate(arg, docstr):
    lines = docstr.splitlines()
    state = False
    for line in lines:
        if "%s : " % arg in line:
            state = "PyoObject" in line
            break
    return state

def get_audio_rate_args(args, docstr):
    mul_add = False
    if "mul" in args:
        mul_add = True
    audioargs = [arg for arg in args if is_audio_rate(arg, docstr)]
    if mul_add:
        audioargs.extend(['mul', 'add'])
    return audioargs

def get_args_list(obj):
    args, vargs, vkw, defs = inspect.getargspec(getattr(eval(obj), "__init__"))
    # arguments to filter out of the list
    for arg in ["self", "input", "input2"]:
        if arg in args:
            args.remove(arg)
    return args

def add_object_to_dict(obj, dict):
    args = get_args_list(obj)
    docstr = get_args_doc(obj)
    dict[obj] = get_audio_rate_args(args, docstr)
    
#remove objects with no audio rate parameters
def clean_dict(dict):
    to_delete = []
    for key in dict:
        if len(dict[key]) == 0:
            to_delete.append(key)
    for elem in to_delete:
        del dict[elem]

# walk down the object tree and construct the dictiobary
final_dict = {}
tree = OBJECTS_TREE
basetree = tree["PyoObjectBase"]
for key in basetree:
    if key == "PyoObject":
        for key2 in basetree[key]:
            for obj in basetree[key][key2]:
                add_object_to_dict(obj, final_dict)
    else:
        for obj in basetree[key]:
            add_object_to_dict(obj, final_dict)
            
clean_dict(final_dict)

with open(OUTPUT_FILE, "w") as f:
    pickle.dump(final_dict, f)

# pretty print the dictionary to OUTPUT_FILE
#with open(OUTPUT_FILE, "w") as f:
#    pprint.pprint(final_dict, f, indent=4, width=150)
