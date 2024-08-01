import os
import sys
import shutil
import gradio as gr
from requests import get
import multiprocessing
import time
from datetime import datetime
# from tkinter import messagebox
import io
import cv2
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
import json
import traceback
import threading
import git
import random
from glob import glob
# fastapi
import uvicorn
from fastapi import Depends, FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response

app = FastAPI()


# # 创建数字分身进程池，进程总数等于使用GPU数量
# gpu_digital_gen_count = 1
# # 使用锁和条件变量维护GPU状态表
# gpu_digital_gen_lock = multiprocessing.Lock()
# gpu_digital_gen_condition = multiprocessing.Condition(lock=gpu_digital_gen_lock)
# # 创建共享的GPU状态字典
# gpu_digital_gen_manager = multiprocessing.Manager()
# gpu_digital_gen_status = gpu_digital_gen_manager.dict({i: True for i in range(gpu_digital_gen_count)})  # 初始时所有GPU都为空闲
#
# # 创建生成图片进程池，进程总数等于使用GPU数量
# images_gen_count = 1
# # 使用锁和条件变量维护GPU状态表
# images_gen_lock = multiprocessing.Lock()
# images_gen_condition = multiprocessing.Condition(lock=images_gen_lock)
# # 创建共享的GPU状态字典
# images_gen_manager = multiprocessing.Manager()
# images_gen_status = images_gen_manager.dict({i: True for i in range(images_gen_count)})  # 初始时所有GPU都为空闲
#
# # 用户上传图片地址记录字典
# ip_upload_images_path_lock = threading.Lock()
# # 初始化用户上传图片地址记录字典
# ip_upload_images_path_records = {}
#
# # 初始化用户风格模板点击记录字典
# ip_choose_template_gallery_records = {}
#
# # 初始化用户风格模板列表记录字典
# ip_template_images_list_records = {}
#
# # 初始化用户风格模板序号对应列表记录字典
# ip_template_images_dict_records = {}
#
# # 初始化用户状态消息记录字典
# ip_status_records = {}
#
# # 初始化用户lora权重记录字典
# ip_lora_records = {}
# # 用户lora权重记录字典锁
# ip_lora_records_lock = threading.Lock()
#
# # 数字分身处理列表
# ip_digital_gen_processing_list = []
#
# # 图片生成处理列表
# ip_images_gen_processing_list = []
#
# # 用户上传小于10张图片会报错
# UPLOADLIMIT = 10
#
# # 实际合格图片小于会报错
# PASSLIMIT = 5
#
# assert PASSLIMIT < UPLOADLIMIT, "PASSLIMIT should be lower than UPLOADLIMIT"
#
# # 用户数字分身个数限制
# NUMBERLIMIT = 10
#
# # 用户命名数字分身长度大于会报错
# LENGTHLIMIT = 14
#
# # 保存图片目录，在该目录会保存用户每次上传的图片
# save_img_root_path = "./save_img_root"
# if not os.path.exists(save_img_root_path):
#     os.mkdir(save_img_root_path)
#
# # 用户权重目录，会在该目录保存用户生成的权重，用于Radio读取
# output_root_path = "./output"
# if not os.path.exists(output_root_path):
#     os.mkdir(output_root_path)
#
# # 工作目录，在该目录会生成src,tmp,tmp2,error_img,tmp_face.jpg,lora,infer_temp,img2img,final_res,outputs
# workspace_root_path = "/data/chenlinfeng/easy_photo_models_and_temp/gradio"
# if not os.path.exists(workspace_root_path):
#     os.mkdir(workspace_root_path)
#
# # 用户上传图片记录目录，会在该目录保存用户每次点击数字分身生成上传的图片
# # backups_root_path = "./backups"
# # if not os.path.exists(backups_root_path):
# #     os.mkdir(backups_root_path)
#
# # 用户权重记录目录，会在该目录保存用户每次生成的权重
# # lora_root_path = "./backups_lora"
# # if not os.path.exists(lora_root_path):
# #     os.mkdir(lora_root_path)
#
# # 用户生成图片结果记录目录，会在该目录保存用户每次点击生成图片的处理结果
# sd_res_output_root_path = "./sd_res"
# if not os.path.exists(sd_res_output_root_path):
#     os.mkdir(sd_res_output_root_path)


css = """
.btn_upload {font-size: 12px !important;}
.output_gallery {height: 800px !important;}
.btn_delete {height: 75px !important;}
.digital_radio {height: 170px !important;}
.btn_refresh {height: 75px !important;}
.btn_reselect {height: 75px !important;margin-top: 5px !important;}
footer {visibility: hidden}
.upload_button {height: 75px !important;margin-top: 5px !important;}
"""

reselect_symbol = '\U000021BB'
delete_symbol = '\U000026D4'
refresh_symbol = '\U0001f504'  # 🔄
upload_symbol = "\U0001f4c2"


def check_file(file):
    return_text = """
角色ID: {bot_id}
角色名字: {char_name}
用户名字: {user_name}
    
{ans}"""
    return_text = return_text.strip()
    try:
        with open(file.name, 'r') as f:
            file_name = os.path.basename(file.name)
            bot_id = file_name.split('_')[0].strip()
            char_name = file_name.split('_')[1].strip()
            user_name = file_name.split('_')[2].strip()

            content = f.read()
            lines = content.split('\n')
            expected_speaker = char_name
            line_number = 0
            issues = []

            for line in lines:
                line_number += 1
                if line.strip() == "":
                    continue  # 跳过空行

                if ':' not in line:
                    continue  # 跳过不包含对话的行

                speaker, dialogue = line.split(':', 1)
                speaker = speaker.strip()
                dialogue = dialogue.strip()

                if speaker != expected_speaker:
                    issues.append(f"问题出现在第 {line_number} 行: {line.strip()}")

                # 切换预期的说话者
                if expected_speaker == char_name:
                    expected_speaker = user_name
                else:
                    expected_speaker = char_name

            if issues:
                return return_text.replace('{bot_id}', bot_id).replace('{char_name}', char_name).replace('{user_name}', user_name).replace('{ans}', "\n".join(issues))
            else:
                return return_text.replace('{bot_id}', bot_id).replace('{char_name}', char_name).replace('{user_name}', user_name).replace('{ans}', "对话内容顺序正确")

    except Exception as e:
        return f"Error reading file: {e}"


def reset_log():
    return ""



if __name__ == "__main__":
    with gr.Blocks(css=css) as demo:
        with gr.Row():
            with gr.Column(scale=1):
                text_intro = gr.HTML(
                    "<div style='margin-top: 20px'><h4>🤗 使用步骤:</h4><ol><li>在下方上传TXT文件方框中上传需要校验的TXT文件，点击Check按钮;</li><li>在右侧日志栏查看结果。如果没有错误，则返回OK。如果有问题，则会打印所有出现问题的行数。</li></ol><p>‼️ 注意: 上传的文件名需要通过'_'来按顺序区分角色ID、角色名字、用户名字，类似于:10084_ヴィクトール_ルカ_胡舒.txt</p>"
                )

                with gr.Row():
                    with gr.Column(scale=1, min_width=50):
                        text = gr.HTML("<p style='text-align: left; font-size: 20px; margin-top: 50px'>"
                                       + "上传: "
                                       + "</p>")

                file_upload = gr.File(label="上传TXT文件", file_types=[".txt"])

                btn_digital_gen = gr.Button(value="Check")


            with gr.Column(scale=2):
                with gr.Group():
                    status_display = gr.Textbox(label="日志", lines=23)

        # f.select(preview, f, i)
        # btn.click(lambda x: x, i, o)
        file_upload.change(reset_log, inputs=None, outputs=status_display)
        btn_digital_gen.click(check_file, inputs=[file_upload], outputs=[status_display])
    demo.queue().launch(server_name="0.0.0.0", server_port=8081)
    # app = gr.mount_gradio_app(app, demo, f'/gradio')
    # uvicorn.run(app, host="0.0.0.0", port=8081)
