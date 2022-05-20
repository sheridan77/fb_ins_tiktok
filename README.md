# fb_ins_tiktok

基于比特多登浏览器的facebook，Instagram，tiktok页面自动化操作程序

### Facebook
1.fb添加推荐好友

2.fb通过好友请求

3.fb邀请好友点赞指定专页

4.fb主页帖子分享

5.fb加入指定小组

6.fb发布帖子

7.fb点赞帖子

使用方法:
```gitexclude
>> git clone https://github.com/sheridan77/fb_ins_tiktok.git
>> cd fb_ins_tiktok
>> python venv venv
>> venv\Scripts\activate
>> pip install -r requirements.txt
```
修改setting.py中的内容

···第一行的base_url,可以在比特浏览器的个人头像处的系统设置中查询到本地接口，复制本地接口url，复制到base_url后面

···第二行facebook_xlsx_path 填写fb_task.xlsx文件的绝对路径(*注:在同一路径下可只填写文件名称)

xlsx内容请根据模板编写，窗口文件id可在比特浏览器指纹设置的最上方的"复制ID"获取
```shell script
>> 使用管理员权限运行facebook_task.py文件, 否则发布帖子上传图片会出现如下报错:
Not enough rights to use WM_*BUTTONDOWN/UP message/function for target process (to resolve it run the script as Administrator)
# python 版本 >= 3.7
>> python facebook_task.py 
```

### Instagram
### Tiktok
