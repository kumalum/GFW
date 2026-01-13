import requests
import argparse
import shutil

import sb
import sb.config
import sb.enum

def downloads(g_name:str, url:str):
    # 获取下载地址， 并创建文件夹
    download_dir = path.downloads.joinpath(g_name)

    try:
        if not download_dir.exists(): 
            download_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return

    # 下载文件
    response = requests.get(url, stream=True)

    file = download_dir.joinpath(url.split("/")[-1] )
    sb.write(response.content, path=file, mode='wb', encoding=None)

def merge_json():
    """ 合并同类型的规则文件，即配置文件 pref.example.toml 中 downloads 同列表的规则 """
    json_list = [f for f in path.downloads.rglob("*") if f.is_file and f.suffix == enum.suffix.json]

    for fjson in json_list:
        rule_set_file_name = fjson.parent.with_suffix(enum.suffix.json).name
        rule_set_file = path.output.joinpath(rule_set_file_name)

        old_rules_content = sb.read(rule_set_file)
        new_rules_content = sb.read(fjson)

        new_rules = new_rules_content[enum.base.rules][0]
        old_rules = old_rules_content[enum.base.rules][0]
        
        for rule in new_rules:
            if rule in old_rules_content:
                old_rules[rule] = list(set(new_rules[rule] + old_rules[rule]))
            else:
                old_rules[rule] = new_rules[rule]

def compile(suffix):
    if suffix == enum.suffix.srs:
        is_compile = "decompile"
        after_suffix = enum.suffix.json

    else:
        is_compile = "compile"
        after_suffix = enum.suffix.srs

    files = [f for f in path.downloads.rglob("*") if f.is_file and f.suffix == suffix]

    for f in files:
        if f.parent.name == enum.group.adguard: continue
        after_file = f.with_suffix(after_suffix)
        cmd = [enum.base.singbox, enum.singbox.rule_set, is_compile, f, "-o", after_file]
        sb.process_script(cmd)

def binary_adguard():
    adguard = [f for f in path.downloads.rglob("*") if f.is_file and f.name == "blocklist"]
    if not adguard: return
    adguard = adguard[0]
    binary = path.output.joinpath("adguard.srs")

    cmd = [enum.base.singbox, enum.singbox.rule_set, "convert", "--type", "adguard", "--output", str(binary), str(adguard)]
    sb.process_script(cmd)


def run():

    if path.output.exists(): shutil.rmtree(path.output)

    group =  pref_config[enum.base.group]
    for g_name in group:
        
        try: 
            urls = group[g_name][enum.base.download]
        except KeyError: 
            continue;
        
        for url in urls: downloads(g_name, url)

    # 二进制文件解码
    compile(enum.suffix.srs)
    merge_json()
    # 转为二进制文件
    compile(enum.suffix.json)

    binary_adguard()

if __name__ == "__main__":
    config = sb.config
    path = config.Path
    pref_config = config.Content.pref_config
    enum = sb.enum

    run()