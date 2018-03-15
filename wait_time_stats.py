from pathlib import Path, PurePath
from collections import OrderedDict
from bs4 import BeautifulSoup
import json

def load_html():
    p = Path('tables')
    html_dict = {}
    for x in p.iterdir():
        if not x.is_dir():
            key = str(x).split('/')[-1].strip('.html')
            html = x.read_text()
            html_dict.setdefault(key, html)
    ordered_html_dict = OrderedDict(sorted(html_dict.items(), key=lambda k: k))
    # print(ordered_html_dict.keys())
    return ordered_html_dict

def extract_wait_time(key, html):
    table_dict = {}
    table_dict.setdefault('date', key)
    soup = BeautifulSoup(html, 'html.parser')
    ## search text 'S平均'
    td = soup.find_all("td", text="S平均")
    tcontain = td[0].parent.parent
    stats_title = []
    stats_content = []
    for item in tcontain.contents[0].children:
        stats_title.append(item.text)
    for item in tcontain.contents[1].children:
        stats_content.append(item.text)
    ## set stats in dict
    table_dict.setdefault('stats', {})
    for i, item in enumerate(stats_title):
        table_dict['stats'].setdefault(item, stats_content[i])
    all_trs = tcontain.parent.parent.parent.parent
    stats_tr = all_trs.contents[1]
    type_tr = all_trs.contents[2]
    name_tr = all_trs.contents[3]
    
    attraction_titles = []
    title_ids = []
    for item in name_tr.children:
        title = item.find('span')['title']
        ttarr = title.split('.')
        real_title = '.'.join(ttarr[1:])
        title_id = ttarr[0]
        attraction_titles.append(real_title)
        title_ids.append(title_id)

    END_FLAG = '21:45'
    count = len(name_tr.contents)
    types = []
    for i, item in enumerate(type_tr.children):
        if i > 1 and i < count + 2:
            types.append(item.text)
    time_slot = []
    wait_time_slot = []
    weather_slot = []
    temp_slot = []
    for i, tr in enumerate(all_trs.contents):
        if i > 3:
            wait_time_row = []
            first_ele = tr.contents[0].text
            # print(first_ele)
            tr_len = len(tr)
            if tr_len == count + 2:
                wait_time_s_idx = 1
            elif tr_len == count + 3:
                temp = tr.contents[1].text
                weather = tr.contents[1].find('img')['src']
                weather_slot.append(weather)
                temp_slot.append(temp)
                wait_time_s_idx = 2
            wait_time_e_idx = wait_time_s_idx + count
            for idx in range(wait_time_s_idx, wait_time_e_idx):
                ele = tr.contents[idx].text
                wait_time_row.append(ele)
    #         print(wait_time_row)
            time_slot.append(first_ele)
            wait_time_slot.append(wait_time_row)
            if first_ele == END_FLAG:
                break
    # print(wait_time_slot)
    # print(time_slot)
    # print(weather_slot)
    # print(temp_slot)
    ## set time slots in dict
    table_dict.setdefault('timeSlots', time_slot)
    ## set time weather and temperature in dict
    table_dict.setdefault('weather', weather_slot)
    table_dict.setdefault('temperature', temp_slot)
    ## set attraction in dict
    table_dict.setdefault('attractions', [])
    for i, item in enumerate(attraction_titles):
        table_dict['attractions'].append({})
        attr = table_dict['attractions'][i]
        attr.setdefault('title', item)
        attr.setdefault('id', title_ids[i])
        attr.setdefault('type', types[i])
        attr.setdefault('waitTime', [])
        for slot in wait_time_slot:
            arr_idx = i
            attr['waitTime'].append(slot[arr_idx])
    return table_dict

def main():
    ordered_html_dict = load_html()
    for key in ordered_html_dict:
        html = ordered_html_dict[key]
        t = extract_wait_time(key, html)
        fp = Path('extracted_json')
        if not fp.exists():
            fp.mkdir()
        p = PurePath('extracted_json', key + '.json')
        with open(str(p), 'w') as outfile:
            json.dump(t, outfile, ensure_ascii=False)

if __name__ == '__main__':
    main()