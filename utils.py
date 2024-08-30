
def message(var_tuple=(), origin_class=None, filename=None, message="", saut_precedant=False, saut_suivant=False):

    """ Comme "print()" mais mieux """

    str_start = ""
    if origin_class:
        str_start = origin_class.class_name
    elif filename:
        str_start = filename
    
    str_start = f"[{str_start}]"

    full_str = ""
    if message:
        full_str = f"{str_start} {message}"
    

    idx = 0
    for arg in var_tuple:
        if idx % 2 == 0:
            full_str += f"\n{str_start} {arg} : "
        else:
            full_str += f"{arg}"

        idx += 1
    
    if saut_precedant:
        print("")

    print(full_str)

    if saut_suivant:
        print("")
