import dxfgrabber as grb

if __name__ == "__main__":
    # 读取dxf文件
    dxf_object = grb.readfile('../data/map/zhenjiang/zhenjiang.dxf')

    for entity in dxf_object.entities:
        if entity.layer == 'ref_line':
            if entity.dxftype != 'LINE' and entity.dxftype != 'ARC':
                print('type = {}'.format(entity.dxftype))
