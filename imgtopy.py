# -*- coding: utf-8 -*-
import base64
def pic2py(picture_name):
    """
         Convert image file to py file
    :param picture_name:
    :return:
    """
    open_pic = open("%s" % picture_name, 'rb')
    b64str = base64.b64encode(open_pic.read())
    open_pic.close()
    write_data = 'img = "%s"' % b64str.decode()
    f = open('%s.py' % picture_name.replace('.', '_'), 'w+')
    f.write(write_data)
    f.close()


if __name__ == '__main__':
    pics = ["gadun.jpg"] # Put the name of the file you want to convert here
    for i in pics:
        pic2py(i)
