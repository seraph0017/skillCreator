import argparse
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def share_resource(token, member_id, member_type, role, type):
    client = FeishuDrive()
    
    # 如果 member_id 是手机号或邮箱，自动推断 member_type
    if not member_type:
        if "@" in member_id:
            member_type = "email"
        elif member_id.isdigit() and len(member_id) > 10: # 简单判断手机号
            member_type = "mobile" # 注意：Permission API 是否直接支持 mobile? 
            # 查阅文档，Permission API 的 member_type 支持: email, openid, userid, unionid, chatid, departmentid
            # 并不直接支持 mobile。如果用户提供 mobile，需要先换取 openid/userid。
            # 为了简化，我们暂时只支持 email 和 id。如果用户输入 mobile，可能需要额外接口 (contact:user:batch_get_id)
            pass
        else:
            member_type = "openid" # 默认

    # 如果是 mobile，提示不支持或尝试转换 (暂不支持转换，需 Contact 权限)
    if member_type == "mobile":
         print("❌ 暂不支持直接使用手机号，请使用 open_id, user_id 或 email")
         return

    result = client.add_member_permission(token, member_id, member_type, role, type)
    
    if result and result.get("code") == 0:
        print(f"✅ 共享成功")
        print(f"资源 Token: {token}")
        print(f"用户: {member_id} ({member_type})")
        print(f"权限: {role}")
    else:
        print(f"❌ 共享失败: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="共享飞书云文档资源 (添加协作者)")
    parser.add_argument("token", help="资源 Token")
    parser.add_argument("member_id", help="用户 ID (OpenID, UserID, Email)")
    parser.add_argument("--type", help="资源类型 (file/docx/sheet/bitable/folder)", default="docx")
    parser.add_argument("--role", help="权限角色 (view, edit, full_access)", default="full_access")
    parser.add_argument("--member_type", help="用户 ID 类型 (openid, userid, email)", default="")
    
    args = parser.parse_args()
    
    share_resource(args.token, args.member_id, args.member_type, args.role, args.type)
