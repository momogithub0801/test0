import os
import streamlit as st


# def check_file(file, filename):
#     return_text = """
# 角色ID: {bot_id}
# 角色名字: {char_name}
# 用户名字: {user_name}
#
# {ans}"""
#     return_text = return_text.strip()
#     try:
#         content = file.read().decode('utf-8')
#         file_name = os.path.basename(filename)
#         bot_id = file_name.split('_')[0].strip()
#         char_name = file_name.split('_')[1].strip()
#         user_name = file_name.split('_')[2].strip()
#
#         lines = content.split('\n')
#         expected_speaker = char_name
#         line_number = 0
#         issues = []
#         # previous_lines = []
#
#         for line in lines:
#             line_number += 1
#             if line.strip() == "":
#                 continue  # 跳过空行
#
#             if ':' not in line:
#                 continue  # 跳过不包含对话的行
#
#             speaker, dialogue = line.split(':', 1)
#             speaker = speaker.strip()
#             dialogue = dialogue.strip()
#
#             if speaker != expected_speaker:
#                 issues.append(f"问题出现在第 {line_number} 行: {line.strip()}")
#             # else:
#             #     print(speaker, expected_speaker, line_number)
#             #
#             # # 检查是否重复
#             # if line.strip() in previous_lines:
#             #     issues.append(f"第 {line_number} 行出现重复，内容是：{line.strip()}")
#
#             # previous_lines.append(line.strip())
#
#             # 切换预期的说话者
#             if expected_speaker == char_name:
#                 expected_speaker = user_name
#                 # previous_lines = []
#
#             else:
#                 expected_speaker = char_name
#                 # previous_lines = []
#
#         if issues:
#             return return_text.replace('{bot_id}', bot_id).replace('{char_name}', char_name).replace('{user_name}',
#                                                                                                      user_name).replace(
#                 '{ans}', "\n".join(issues))
#         else:
#             return return_text.replace('{bot_id}', bot_id).replace('{char_name}', char_name).replace('{user_name}',
#                                                                                                      user_name).replace(
#                 '{ans}', "对话内容顺序正确")
#
#     except Exception as e:
#         return f"Error reading file: {e}"


def check_file_new(file):
    return_text = """
角色ID: {bot_id}
角色名字: {char_name}
用户名字: {user_name}

{ans}"""
    return_text = return_text.strip()
    try:
        with open(file, 'r') as read_file:
            content = read_file.read()
        file_name = os.path.basename(file)
        bot_id = file_name.split('_')[0].strip()
        char_name = file_name.split('_')[1].strip()
        user_name = file_name.split('_')[2].strip()

        lines = content.split('\n')
        expected_speaker = char_name
        line_number = 0
        issues = []
        previous_lines = []
        msg_cnt = 0
        for line in lines:
            line_number += 1
            if line.strip() == "":
                continue  # 跳过空行

            if ':' not in line:
                continue  # 跳过不包含对话的行

            msg_cnt += 1

            speaker, dialogue = line.split(':', 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()

            # if speaker != expected_speaker:
            #     issues.append(f"问题出现在第 {line_number} 行: {line.strip()}")
            if speaker != expected_speaker and msg_cnt == 1:
                issues.append(f"[第一句话不是Bot] 问题出现在第 {line_number} 行: {line.strip()}")
            # else:
            #     print(speaker, expected_speaker, line_number)

            # 检查是否重复
            if previous_lines:
                split_index = line.strip().find(':')
                line_role = line[:split_index]
                split_index = previous_lines[0].find(':')
                pre_role = previous_lines[0][:split_index]
                if line_role == pre_role:
                    issues.append(f"第 {line_number} 行出现重复，内容是：{line.strip()}")

            previous_lines.append(line.strip())

            # 切换预期的说话者
            if expected_speaker == char_name:
                expected_speaker = user_name
                previous_lines = [line]

            else:
                expected_speaker = char_name
                previous_lines = [line]

        if issues:
            return return_text.replace('{bot_id}', bot_id).replace('{char_name}', char_name).replace('{user_name}',
                                                                                                     user_name).replace(
                '{ans}', "\n".join(issues))
        else:
            return return_text.replace('{bot_id}', bot_id).replace('{char_name}', char_name).replace('{user_name}',
                                                                                                     user_name).replace(
                '{ans}', "对话内容顺序正确")

    except Exception as e:
        return f"Error reading file: {e}"


st.title("TXT文件校验工具")

st.markdown("""
### 🤗 使用步骤:
1. 在下方上传TXT文件方框中上传需要校验的TXT文件，点击Check按钮;
2. 在弹出的日志中查看结果。如果没有错误，则返回没有问题。如果有问题，则会打印所有出现问题的行数。

‼️ 注意: 上传的文件名需要通过'_'来按顺序区分角色ID、角色名字、用户名字，类似于:10084_ヴィクトール_ルカ_胡舒.txt
""")

uploaded_file = st.file_uploader("上传TXT文件", type="txt")

if uploaded_file is not None:
    filename = uploaded_file.name
    st.text(f"文件名: {filename}")
    if st.button("Check"):
        result = check_file_new(uploaded_file, filename)
        st.text_area("日志", result, height=400)