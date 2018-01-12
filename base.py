# -*- coding: utf-8 -*-
import sys,os,datetime,math,csv,urllib2,json
reload(sys)
sys.setdefaultencoding("utf-8")
from baidumap import BaiduMap
second_format = "%Y-%m-%d %H:%M:%S"
dt_start = datetime.datetime.strptime("2017-03-01 00:00:00", second_format)
def datetime_compare(item1, item2):
    t1 = datetime.datetime.strptime(item1, second_format)
    t2 = datetime.datetime.strptime(item2, second_format)
    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    else:
        return 0
def import_call_accident_data_from_json(input_json_filepath,input_acc_db_tsv_fp,out_loc_fp,out_place_fp):
    final_preserve = {}
    with open(input_acc_db_tsv_fp, "rb") as input_file:
        reader = csv.reader(input_file)
        for utf8_row in reader:
            create_time_str, lng, lat, place = utf8_row[0].decode('utf8').split("\t")
            create_time_str = create_time_str.split(".")[0]
            place = place.strip("\n")
            final_preserve[create_time_str] = [create_time_str, lng, lat, place]
    print "finish handle %s" % input_acc_db_tsv_fp
    bdmap = BaiduMap("北京市")
    input_file = open(input_json_filepath,"r")
    input_str = input_file.read().decode("utf-8")
    json_obj = json.loads(input_str)
    print "finish load %s" % input_json_filepath
    num = 1
    print "json len %d" % len(json_obj)
    for item in json_obj:
        num += 1
        if num % 100 == 0:
            print "processed %d 122 data" % num
        create_time_str, accident_content, place = item
        create_time = datetime.datetime.strptime(create_time_str, second_format)
        if create_time < dt_start:
            continue
        try:
            bd_point = bdmap.getLocation(place)
            if bd_point is None:
                continue
            # 可信度小于50%丢弃
            if bd_point[2] <= 50:
                continue
            longitude = bd_point[0]
            latitude = bd_point[1]
            final_preserve[create_time_str] = [create_time_str,str(longitude),str(latitude),place]
        except Exception as e:
            print("---bdmap error!! info:" + str(e))
            continue
    print "finish baidu, start sorting"
    data_sorted = sorted(final_preserve.items(), key=lambda d: d[0])
    print "finish sorting"
    item_i = 0
    locs = []
    places = []
    for key, item in data_sorted:
        item_i += 1
        create_time_str, lng, lat, place = item
        locs.append("\t".join([str(item_i),create_time_str, lng, lat]))
        places.append("\t".join([str(item_i),create_time_str, place]))
    with open(out_loc_fp, "w") as out_loc_file:
        out_loc_file.write("\n".join(locs))
    print "write %s successful" % out_loc_fp

    with open(out_place_fp, "w") as out_place_file:
        out_place_file.write("\n".join(places))
    print "write %s successful" % out_place_fp

if __name__ == "__main__":
    input_json_filepath = "data/122_2017.json"
    out_loc_fp = "data/accident_loc.tsv"
    out_place_fp = "data/accident_place.tsv"
    input_acc_db_tsv_fp = "data/accident_from_db.tsv"
    import_call_accident_data_from_json(input_json_filepath,input_acc_db_tsv_fp,out_loc_fp,out_place_fp)
